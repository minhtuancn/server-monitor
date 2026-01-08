# Project Review Report

**Generated:** 2026-01-08 05:29:21 UTC  
**Ref:** main  
**Commit:** cc071e1 (cc071e175b3b77e402e13b564a676e107ef4c678)  
**Branch:** main  
**Author:** Minh Tuấn <vietkeynet@gmail.com>  
**Date:** 2026-01-08 12:21:55 +0700

---

## Executive Summary

This automated review report provides a comprehensive audit of the server-monitor project, including code quality checks, test results, build validation, and documentation consistency.

### Quick Status

| Component | Status |
|-----------|--------|
| Python Linting | ⚠️ UNKNOWN |
| Unit Tests | ⚠️ UNKNOWN |
| Frontend Build | ⚠️ UNKNOWN |
| Smoke Tests | ⚠️ UNKNOWN |
| UI Screenshots | ⚠️ SKIPPED |

---

## Environment Information

- **Runner OS:** Linux
- **Python Version:** Python 3.12.3
- **Node Version:** v20.19.6
- **Git Version:** git version 2.52.0

---

## Repository Statistics

- **Backend Python Files:** 32
- **Frontend TypeScript Files:** 41
- **Test Files:** 9
- **Documentation Files:** 31

---

## CI Results

### 1. Static Analysis & Linting

**Python Linting (flake8):** ⚠️ UNKNOWN

#### Details:
```
=== Python Linting (flake8) ===
backend/central_api.py:352:32: F823 local variable 'metrics' defined in enclosing scope on line 52 referenced before assignment
                json_metrics = metrics.get_metrics()
                               ^
backend/central_api.py:3548:5: F824 `global http_server` is unused: name is never assigned in scope
    global http_server
    ^
backend/database.py:2869:12: F821 undefined name 'get_db'
    conn = get_db()
           ^
backend/database.py:2889:12: F821 undefined name 'get_db'
    conn = get_db()
           ^
backend/database.py:2915:12: F821 undefined name 'get_db'
    conn = get_db()
           ^
backend/task_runner.py:229:16: F821 undefined name 'socket'
        except socket.timeout as e:
               ^
backend/terminal.py:538:5: F824 `global ws_server` is unused: name is never assigned in scope
    global ws_server
    ^
backend/websocket_server.py:262:5: F824 `global ws_server` is unused: name is never assigned in scope
    global ws_server
    ^
backend/websocket_server.py:301:5: F824 `global ws_server` is unused: name is never assigned in scope
    global ws_server
    ^
4     F821 undefined name 'get_db'
1     F823 local variable 'metrics' defined in enclosing scope on line 52 referenced before assignment
4     F824 `global http_server` is unused: name is never assigned in scope
9
backend/agent.py:36:1: E302 expected 2 blank lines, found 1
backend/agent.py:41:5: E722 do not use bare 'except'
backend/agent.py:44:1: E302 expected 2 blank lines, found 1
backend/agent.py:52:1: W293 blank line contains whitespace
backend/agent.py:55:1: W293 blank line contains whitespace
backend/agent.py:58:1: W293 blank line contains whitespace
backend/agent.py:61:1: W293 blank line contains whitespace
backend/agent.py:64:1: W293 blank line contains whitespace
backend/agent.py:68:1: W293 blank line contains whitespace
backend/agent.py:74:1: W293 blank line contains whitespace
backend/agent.py:81:1: W293 blank line contains whitespace
backend/agent.py:88:1: W293 blank line contains whitespace
backend/agent.py:98:1: W293 blank line contains whitespace
backend/agent.py:109:1: E302 expected 2 blank lines, found 1
backend/agent.py:118:1: W293 blank line contains whitespace
backend/agent.py:126:1: W293 blank line contains whitespace
backend/agent.py:131:1: W293 blank line contains whitespace
backend/agent.py:136:1: W293 blank line contains whitespace
backend/agent.py:139:1: W293 blank line contains whitespace
backend/agent.py:144:1: W293 blank line contains whitespace
backend/agent.py:168:1: E302 expected 2 blank lines, found 1
backend/agent.py:171:1: W293 blank line contains whitespace
backend/agent.py:175:1: W293 blank line contains whitespace
backend/agent.py:182:1: W293 blank line contains whitespace
backend/agent.py:185:1: W293 blank line contains whitespace
backend/agent.py:192:1: W293 blank line contains whitespace
backend/agent.py:198:1: W293 blank line contains whitespace
backend/agent.py:204:1: W293 blank line contains whitespace
backend/agent.py:207:1: W293 blank line contains whitespace
backend/agent.py:216:1: E302 expected 2 blank lines, found 1
backend/agent.py:219:1: W293 blank line contains whitespace
backend/agent.py:223:1: W293 blank line contains whitespace
backend/agent.py:227:1: W293 blank line contains whitespace
backend/agent.py:232:1: W293 blank line contains whitespace
backend/agent.py:235:1: W293 blank line contains whitespace
backend/agent.py:242:1: W293 blank line contains whitespace
backend/agent.py:248:1: W293 blank line contains whitespace
backend/agent.py:254:1: W293 blank line contains whitespace
backend/agent.py:261:1: E302 expected 2 blank lines, found 1
backend/agent.py:265:1: W293 blank line contains whitespace
backend/agent.py:277:1: W293 blank line contains whitespace
backend/agent.py:280:1: E302 expected 2 blank lines, found 1
backend/agent.py:288:1: W293 blank line contains whitespace
backend/agent.py:297:1: W293 blank line contains whitespace
backend/agent.py:300:1: E302 expected 2 blank lines, found 1
backend/agent.py:301:1: W293 blank line contains whitespace
backend/agent.py:307:1: W293 blank line contains whitespace
backend/agent.py:312:1: W293 blank line contains whitespace
backend/agent.py:317:1: W293 blank line contains whitespace
backend/agent.py:322:1: W293 blank line contains whitespace
backend/agent.py:327:1: W293 blank line contains whitespace
backend/agent.py:332:1: W293 blank line contains whitespace
backend/agent.py:337:1: W293 blank line contains whitespace
backend/agent.py:349:1: W293 blank line contains whitespace
backend/agent.py:353:1: W293 blank line contains whitespace
backend/agent.py:357:1: E305 expected 2 blank lines after class or function definition, found 1
backend/alert_manager.py:14:1: E402 module level import not at top of file
backend/alert_manager.py:15:1: E402 module level import not at top of file
backend/alert_manager.py:16:1: E402 module level import not at top of file
backend/alert_manager.py:17:1: E402 module level import not at top of file
backend/alert_manager.py:18:1: F401 'datetime.datetime' imported but unused
backend/alert_manager.py:18:1: E402 module level import not at top of file
backend/alert_manager.py:32:1: W293 blank line contains whitespace
backend/alert_manager.py:36:1: W293 blank line contains whitespace
backend/alert_manager.py:40:1: W293 blank line contains whitespace
backend/alert_manager.py:44:1: W293 blank line contains whitespace
backend/alert_manager.py:51:1: W293 blank line contains whitespace
backend/alert_manager.py:58:1: W293 blank line contains whitespace
backend/alert_manager.py:67:1: W293 blank line contains whitespace
backend/alert_manager.py:70:1: W293 blank line contains whitespace
backend/alert_manager.py:86:1: W293 blank line contains whitespace
backend/alert_manager.py:102:1: W293 blank line contains whitespace
backend/alert_manager.py:118:1: W293 blank line contains whitespace
backend/alert_manager.py:131:1: W293 blank line contains whitespace
backend/alert_manager.py:138:1: W293 blank line contains whitespace
backend/alert_manager.py:144:1: W293 blank line contains whitespace
backend/alert_manager.py:150:1: W293 blank line contains whitespace
backend/alert_manager.py:152:1: W293 blank line contains whitespace
backend/alert_manager.py:159:1: W293 blank line contains whitespace
backend/alert_manager.py:175:1: W293 blank line contains whitespace
backend/alert_manager.py:182:1: W293 blank line contains whitespace
backend/alert_manager.py:198:1: W293 blank line contains whitespace
backend/alert_manager.py:205:1: W293 blank line contains whitespace
backend/alert_manager.py:221:1: W293 blank line contains whitespace
backend/alert_manager.py:228:1: W293 blank line contains whitespace
backend/alert_manager.py:231:1: W293 blank line contains whitespace
backend/alert_manager.py:239:1: W293 blank line contains whitespace
backend/alert_manager.py:241:1: W293 blank line contains whitespace
backend/alert_manager.py:252:1: W293 blank line contains whitespace
backend/alert_manager.py:263:1: W293 blank line contains whitespace
backend/alert_manager.py:274:1: W293 blank line contains whitespace
backend/alert_manager.py:281:1: W293 blank line contains whitespace
backend/alert_manager.py:288:1: W293 blank line contains whitespace
backend/alert_manager.py:292:1: W293 blank line contains whitespace
backend/audit_cleanup.py:16:1: E402 module level import not at top of file
backend/audit_cleanup.py:17:1: E402 module level import not at top of file
backend/audit_cleanup.py:40:1: W293 blank line contains whitespace
backend/audit_cleanup.py:44:1: W293 blank line contains whitespace
backend/audit_cleanup.py:55:1: W293 blank line contains whitespace
backend/audit_cleanup.py:62:1: W293 blank line contains whitespace
backend/audit_cleanup.py:68:1: W293 blank line contains whitespace
backend/audit_cleanup.py:74:1: W293 blank line contains whitespace
backend/audit_cleanup.py:76:1: W293 blank line contains whitespace
backend/audit_cleanup.py:83:1: W293 blank line contains whitespace
backend/audit_cleanup.py:91:1: W293 blank line contains whitespace
backend/audit_cleanup.py:108:1: W293 blank line contains whitespace
backend/audit_cleanup.py:115:1: W293 blank line contains whitespace
backend/audit_cleanup.py:120:1: W293 blank line contains whitespace
backend/audit_cleanup.py:128:1: W293 blank line contains whitespace
backend/audit_cleanup.py:132:1: W293 blank line contains whitespace
backend/audit_cleanup.py:138:1: W293 blank line contains whitespace
backend/audit_cleanup.py:142:1: W293 blank line contains whitespace
backend/audit_cleanup.py:146:1: W293 blank line contains whitespace
backend/audit_cleanup.py:151:1: W293 blank line contains whitespace
backend/audit_cleanup.py:154:1: W293 blank line contains whitespace
backend/audit_cleanup.py:157:1: W293 blank line contains whitespace
backend/audit_cleanup.py:162:1: W293 blank line contains whitespace
backend/audit_cleanup.py:196:1: W293 blank line contains whitespace
backend/audit_cleanup.py:199:1: W293 blank line contains whitespace
backend/cache_helper.py:16:1: E722 do not use bare 'except'
backend/cache_helper.py:30:1: W293 blank line contains whitespace
backend/cache_helper.py:37:1: W293 blank line contains whitespace
backend/cache_helper.py:43:1: W293 blank line contains whitespace
backend/cache_helper.py:47:1: W293 blank line contains whitespace
backend/cache_helper.py:50:1: W293 blank line contains whitespace
backend/cache_helper.py:56:1: W293 blank line contains whitespace
backend/cache_helper.py:61:1: W293 blank line contains whitespace
backend/cache_helper.py:69:1: W293 blank line contains whitespace
backend/cache_helper.py:74:1: W293 blank line contains whitespace
backend/cache_helper.py:80:13: E722 do not use bare 'except'
backend/cache_helper.py:82:1: W293 blank line contains whitespace
backend/cache_helper.py:86:1: W293 blank line contains whitespace
backend/cache_helper.py:95:1: W293 blank line contains whitespace
backend/cache_helper.py:99:1: W293 blank line contains whitespace
backend/cache_helper.py:106:1: W293 blank line contains whitespace
backend/cache_helper.py:113:1: W293 blank line contains whitespace
backend/cache_helper.py:117:1: W293 blank line contains whitespace
backend/cache_helper.py:124:1: W293 blank line contains whitespace
backend/cache_helper.py:132:1: W293 blank line contains whitespace
backend/cache_helper.py:143:1: W293 blank line contains whitespace
backend/cache_helper.py:147:1: W293 blank line contains whitespace
backend/cache_helper.py:152:1: W293 blank line contains whitespace
backend/cache_helper.py:160:1: W293 blank line contains whitespace
backend/cache_helper.py:163:1: W293 blank line contains whitespace
backend/cache_helper.py:166:1: W293 blank line contains whitespace
backend/cache_helper.py:178:1: W293 blank line contains whitespace
backend/cache_helper.py:183:1: W293 blank line contains whitespace
backend/cache_helper.py:188:1: W293 blank line contains whitespace
backend/central_api.py:21:1: E402 module level import not at top of file
backend/central_api.py:22:1: E402 module level import not at top of file
backend/central_api.py:23:1: E402 module level import not at top of file
backend/central_api.py:24:1: E402 module level import not at top of file
backend/central_api.py:25:1: E402 module level import not at top of file
backend/central_api.py:26:1: E402 module level import not at top of file
backend/central_api.py:27:1: E402 module level import not at top of file
backend/central_api.py:28:1: E402 module level import not at top of file
backend/central_api.py:29:1: E402 module level import not at top of file
backend/central_api.py:30:1: E402 module level import not at top of file
backend/central_api.py:31:1: E402 module level import not at top of file
backend/central_api.py:32:1: E402 module level import not at top of file
backend/central_api.py:33:22: W291 trailing whitespace
backend/central_api.py:34:20: W291 trailing whitespace
backend/central_api.py:35:17: W291 trailing whitespace
backend/central_api.py:38:1: E402 module level import not at top of file
backend/central_api.py:39:1: F401 'task_policy.TaskPolicyViolation' imported but unused
backend/central_api.py:39:1: E402 module level import not at top of file
backend/central_api.py:40:1: E402 module level import not at top of file
backend/central_api.py:41:1: E402 module level import not at top of file
backend/central_api.py:42:1: E402 module level import not at top of file
backend/central_api.py:43:1: F401 'event_model.Event' imported but unused
backend/central_api.py:43:1: E402 module level import not at top of file
backend/central_api.py:44:1: E402 module level import not at top of file
backend/central_api.py:45:1: E402 module level import not at top of file
backend/central_api.py:46:1: E402 module level import not at top of file
backend/central_api.py:77:1: E302 expected 2 blank lines, found 1
backend/central_api.py:77:103: W291 trailing whitespace
backend/central_api.py:78:25: E128 continuation line under-indented for visual indent
backend/central_api.py:81:1: W293 blank line contains whitespace
backend/central_api.py:95:1: W293 blank line contains whitespace
backend/central_api.py:110:1: W293 blank line contains whitespace
backend/central_api.py:113:1: W293 blank line contains whitespace
backend/central_api.py:120:21: E128 continuation line under-indented for visual indent
backend/central_api.py:121:21: E128 continuation line under-indented for visual indent
backend/central_api.py:122:1: W293 blank line contains whitespace
backend/central_api.py:125:1: E302 expected 2 blank lines, found 1
backend/central_api.py:132:1: E302 expected 2 blank lines, found 1
backend/central_api.py:135:1: W293 blank line contains whitespace
backend/central_api.py:140:1: W293 blank line contains whitespace
backend/central_api.py:144:1: W293 blank line contains whitespace
backend/central_api.py:146:1: W293 blank line contains whitespace
backend/central_api.py:157:1: W293 blank line contains whitespace
backend/central_api.py:162:1: E302 expected 2 blank lines, found 1
backend/central_api.py:163:1: W293 blank line contains whitespace
backend/central_api.py:169:1: W293 blank line contains whitespace
backend/central_api.py:173:1: W293 blank line contains whitespace
backend/central_api.py:178:1: W293 blank line contains whitespace
backend/central_api.py:181:1: W293 blank line contains whitespace
backend/central_api.py:185:1: W293 blank line contains whitespace
backend/central_api.py:192:1: W293 blank line contains whitespace
backend/central_api.py:194:1: W293 blank line contains whitespace
backend/central_api.py:199:1: W293 blank line contains whitespace
backend/central_api.py:204:1: W293 blank line contains whitespace
backend/central_api.py:207:1: W293 blank line contains whitespace
backend/central_api.py:210:1: W293 blank line contains whitespace
backend/central_api.py:222:1: W293 blank line contains whitespace
backend/central_api.py:225:1: W293 blank line contains whitespace
backend/central_api.py:228:1: W293 blank line contains whitespace
backend/central_api.py:236:1: W293 blank line contains whitespace
backend/central_api.py:239:1: W293 blank line contains whitespace
backend/central_api.py:245:1: W293 blank line contains whitespace
backend/central_api.py:249:9: E722 do not use bare 'except'
backend/central_api.py:251:1: W293 blank line contains whitespace
backend/central_api.py:252:5: C901 'CentralAPIHandler.do_GET' is too complex (201)
backend/central_api.py:254:1: W293 blank line contains whitespace
backend/central_api.py:262:1: W293 blank line contains whitespace
backend/central_api.py:266:1: W293 blank line contains whitespace
backend/central_api.py:268:1: W293 blank line contains whitespace
backend/central_api.py:276:1: W293 blank line contains whitespace
backend/central_api.py:285:1: W293 blank line contains whitespace
backend/central_api.py:289:1: W293 blank line contains whitespace
backend/central_api.py:293:1: W293 blank line contains whitespace
backend/central_api.py:300:1: W293 blank line contains whitespace
backend/central_api.py:306:1: W293 blank line contains whitespace
backend/central_api.py:311:13: E722 do not use bare 'except'
backend/central_api.py:313:1: W293 blank line contains whitespace
backend/central_api.py:321:13: E722 do not use bare 'except'
backend/central_api.py:323:1: W293 blank line contains whitespace
backend/central_api.py:327:13: E722 do not use bare 'except'
backend/central_api.py:329:1: W293 blank line contains whitespace
backend/central_api.py:335:13: E722 do not use bare 'except'
backend/central_api.py:337:1: W293 blank line contains whitespace
backend/central_api.py:352:32: F823 local variable 'metrics' defined in enclosing scope on line 52 referenced before assignment
backend/central_api.py:357:1: W293 blank line contains whitespace
backend/central_api.py:359:1: W293 blank line contains whitespace
backend/central_api.py:363:1: W293 blank line contains whitespace
backend/central_api.py:377:1: W293 blank line contains whitespace
backend/central_api.py:379:1: W293 blank line contains whitespace
backend/central_api.py:387:1: W293 blank line contains whitespace
backend/central_api.py:392:1: W293 blank line contains whitespace
backend/central_api.py:397:1: W293 blank line contains whitespace
backend/central_api.py:403:1: W293 blank line contains whitespace
backend/central_api.py:408:1: W293 blank line contains whitespace
backend/central_api.py:414:1: W293 blank line contains whitespace
backend/central_api.py:426:1: W293 blank line contains whitespace
backend/central_api.py:433:1: W293 blank line contains whitespace
backend/central_api.py:435:1: W293 blank line contains whitespace
backend/central_api.py:443:1: W293 blank line contains whitespace
backend/central_api.py:448:1: W293 blank line contains whitespace
backend/central_api.py:453:1: W293 blank line contains whitespace
backend/central_api.py:461:1: W293 blank line contains whitespace
backend/central_api.py:468:1: W293 blank line contains whitespace
backend/central_api.py:481:1: W293 blank line contains whitespace
backend/central_api.py:581:1: W293 blank line contains whitespace
backend/central_api.py:583:1: W293 blank line contains whitespace
backend/central_api.py:587:1: W293 blank line contains whitespace
backend/central_api.py:590:1: W293 blank line contains whitespace
backend/central_api.py:597:1: W293 blank line contains whitespace
backend/central_api.py:600:1: W293 blank line contains whitespace
backend/central_api.py:606:1: W293 blank line contains whitespace
backend/central_api.py:609:1: W293 blank line contains whitespace
backend/central_api.py:612:1: W293 blank line contains whitespace
backend/central_api.py:616:1: W293 blank line contains whitespace
backend/central_api.py:625:1: W293 blank line contains whitespace
backend/central_api.py:629:1: W293 blank line contains whitespace
backend/central_api.py:640:1: W293 blank line contains whitespace
backend/central_api.py:649:1: W293 blank line contains whitespace
backend/central_api.py:659:1: W293 blank line contains whitespace
backend/central_api.py:665:1: W293 blank line contains whitespace
backend/central_api.py:675:1: W293 blank line contains whitespace
backend/central_api.py:679:1: W293 blank line contains whitespace
backend/central_api.py:686:1: W293 blank line contains whitespace
backend/central_api.py:689:1: W293 blank line contains whitespace
backend/central_api.py:692:1: W293 blank line contains whitespace
backend/central_api.py:695:1: W293 blank line contains whitespace
backend/central_api.py:697:1: W293 blank line contains whitespace
backend/central_api.py:705:1: W293 blank line contains whitespace
backend/central_api.py:716:1: W293 blank line contains whitespace
backend/central_api.py:724:1: W293 blank line contains whitespace
backend/central_api.py:735:1: W293 blank line contains whitespace
backend/central_api.py:743:1: W293 blank line contains whitespace
backend/central_api.py:747:1: W293 blank line contains whitespace
backend/central_api.py:753:1: W293 blank line contains whitespace
backend/central_api.py:775:1: W293 blank line contains whitespace
backend/central_api.py:783:1: W293 blank line contains whitespace
backend/central_api.py:788:1: W293 blank line contains whitespace
backend/central_api.py:799:1: W293 blank line contains whitespace
backend/central_api.py:801:1: W293 blank line contains whitespace
backend/central_api.py:805:1: W293 blank line contains whitespace
backend/central_api.py:809:1: W293 blank line contains whitespace
backend/central_api.py:814:1: W293 blank line contains whitespace
backend/central_api.py:825:1: W293 blank line contains whitespace
backend/central_api.py:829:1: W293 blank line contains whitespace
backend/central_api.py:838:1: W293 blank line contains whitespace
backend/central_api.py:845:1: W293 blank line contains whitespace
backend/central_api.py:851:1: W293 blank line contains whitespace
backend/central_api.py:858:1: W293 blank line contains whitespace
backend/central_api.py:865:1: W293 blank line contains whitespace
backend/central_api.py:871:1: W293 blank line contains whitespace
backend/central_api.py:877:1: W293 blank line contains whitespace
backend/central_api.py:881:1: W293 blank line contains whitespace
backend/central_api.py:885:1: W293 blank line contains whitespace
backend/central_api.py:888:1: W293 blank line contains whitespace
backend/central_api.py:892:1: W293 blank line contains whitespace
backend/central_api.py:895:1: W293 blank line contains whitespace
backend/central_api.py:905:1: W293 blank line contains whitespace
backend/central_api.py:916:1: W293 blank line contains whitespace
backend/central_api.py:923:1: W293 blank line contains whitespace
backend/central_api.py:929:1: W293 blank line contains whitespace
backend/central_api.py:938:1: W293 blank line contains whitespace
backend/central_api.py:952:1: W293 blank line contains whitespace
backend/central_api.py:954:1: W293 blank line contains whitespace
backend/central_api.py:956:1: W293 blank line contains whitespace
backend/central_api.py:962:1: W293 blank line contains whitespace
backend/central_api.py:964:1: W293 blank line contains whitespace
backend/central_api.py:969:1: W293 blank line contains whitespace
backend/central_api.py:972:1: W293 blank line contains whitespace
backend/central_api.py:975:1: W293 blank line contains whitespace
backend/central_api.py:977:1: W293 blank line contains whitespace
backend/central_api.py:984:1: W293 blank line contains whitespace
backend/central_api.py:991:1: W293 blank line contains whitespace
backend/central_api.py:1001:1: W293 blank line contains whitespace
backend/central_api.py:1003:1: W293 blank line contains whitespace
backend/central_api.py:1011:1: W293 blank line contains whitespace
backend/central_api.py:1018:1: W293 blank line contains whitespace
backend/central_api.py:1026:1: W293 blank line contains whitespace
backend/central_api.py:1034:1: W293 blank line contains whitespace
backend/central_api.py:1041:1: W293 blank line contains whitespace
backend/central_api.py:1045:1: W293 blank line contains whitespace
backend/central_api.py:1056:1: W293 blank line contains whitespace
backend/central_api.py:1057:9: E303 too many blank lines (2)
backend/central_api.py:1058:1: W293 blank line contains whitespace
backend/central_api.py:1066:1: W293 blank line contains whitespace
backend/central_api.py:1069:1: W293 blank line contains whitespace
backend/central_api.py:1079:1: W293 blank line contains whitespace
backend/central_api.py:1088:1: W293 blank line contains whitespace
backend/central_api.py:1099:1: W293 blank line contains whitespace
backend/central_api.py:1110:1: W293 blank line contains whitespace
backend/central_api.py:1118:1: W293 blank line contains whitespace
backend/central_api.py:1121:1: W293 blank line contains whitespace
backend/central_api.py:1123:1: W293 blank line contains whitespace
backend/central_api.py:1126:1: W293 blank line contains whitespace
backend/central_api.py:1131:1: W293 blank line contains whitespace
backend/central_api.py:1137:1: W293 blank line contains whitespace
backend/central_api.py:1143:1: W293 blank line contains whitespace
backend/central_api.py:1145:1: W293 blank line contains whitespace
backend/central_api.py:1153:1: W293 blank line contains whitespace
backend/central_api.py:1163:1: W293 blank line contains whitespace
backend/central_api.py:1165:1: W293 blank line contains whitespace
backend/central_api.py:1173:1: W293 blank line contains whitespace
backend/central_api.py:1180:1: W293 blank line contains whitespace
backend/central_api.py:1186:1: W293 blank line contains whitespace
backend/central_api.py:1190:1: W293 blank line contains whitespace
backend/central_api.py:1196:1: W293 blank line contains whitespace
backend/central_api.py:1202:1: W293 blank line contains whitespace
backend/central_api.py:1204:1: W293 blank line contains whitespace
backend/central_api.py:1212:1: W293 blank line contains whitespace
backend/central_api.py:1219:1: W293 blank line contains whitespace
backend/central_api.py:1229:1: W293 blank line contains whitespace
backend/central_api.py:1239:1: W293 blank line contains whitespace
backend/central_api.py:1250:1: W293 blank line contains whitespace
backend/central_api.py:1252:1: W293 blank line contains whitespace
backend/central_api.py:1261:1: W293 blank line contains whitespace
backend/central_api.py:1267:1: W293 blank line contains whitespace
backend/central_api.py:1270:1: W293 blank line contains whitespace
backend/central_api.py:1275:1: W293 blank line contains whitespace
backend/central_api.py:1284:1: W293 blank line contains whitespace
backend/central_api.py:1293:1: W293 blank line contains whitespace
backend/central_api.py:1299:1: W293 blank line contains whitespace
backend/central_api.py:1304:1: W293 blank line contains whitespace
backend/central_api.py:1308:1: W293 blank line contains whitespace
backend/central_api.py:1316:1: W293 blank line contains whitespace
backend/central_api.py:1323:1: W293 blank line contains whitespace
backend/central_api.py:1337:1: W293 blank line contains whitespace
backend/central_api.py:1346:1: W293 blank line contains whitespace
backend/central_api.py:1352:1: W293 blank line contains whitespace
backend/central_api.py:1356:1: W293 blank line contains whitespace
backend/central_api.py:1362:1: W293 blank line contains whitespace
backend/central_api.py:1366:1: W293 blank line contains whitespace
backend/central_api.py:1375:1: W293 blank line contains whitespace
backend/central_api.py:1383:1: W293 blank line contains whitespace
backend/central_api.py:1390:1: W293 blank line contains whitespace
backend/central_api.py:1399:1: W293 blank line contains whitespace
backend/central_api.py:1409:1: W293 blank line contains whitespace
backend/central_api.py:1433:1: W293 blank line contains whitespace
backend/central_api.py:1440:1: W293 blank line contains whitespace
backend/central_api.py:1455:1: W293 blank line contains whitespace
backend/central_api.py:1463:1: W293 blank line contains whitespace
backend/central_api.py:1470:1: W293 blank line contains whitespace
backend/central_api.py:1479:1: W293 blank line contains whitespace
backend/central_api.py:1489:1: W293 blank line contains whitespace
backend/central_api.py:1511:1: W293 blank line contains whitespace
backend/central_api.py:1518:1: W293 blank line contains whitespace
backend/central_api.py:1533:1: W293 blank line contains whitespace
backend/central_api.py:1541:1: W293 blank line contains whitespace
backend/central_api.py:1545:1: W293 blank line contains whitespace
backend/central_api.py:1547:1: W293 blank line contains whitespace
backend/central_api.py:1554:1: W293 blank line contains whitespace
backend/central_api.py:1558:1: W293 blank line contains whitespace
backend/central_api.py:1563:1: W293 blank line contains whitespace
backend/central_api.py:1568:1: W293 blank line contains whitespace
backend/central_api.py:1575:25: E722 do not use bare 'except'
backend/central_api.py:1577:1: W293 blank line contains whitespace
backend/central_api.py:1579:1: W293 blank line contains whitespace
backend/central_api.py:1584:1: W293 blank line contains whitespace
backend/central_api.py:1587:1: W293 blank line contains whitespace
backend/central_api.py:1593:1: W293 blank line contains whitespace
backend/central_api.py:1595:1: W293 blank line contains whitespace
backend/central_api.py:1612:1: W293 blank line contains whitespace
backend/central_api.py:1666:1: W293 blank line contains whitespace
backend/central_api.py:1671:1: W293 blank line contains whitespace
backend/central_api.py:1672:5: C901 'CentralAPIHandler.do_POST' is too complex (175)
backend/central_api.py:1674:1: W293 blank line contains whitespace
backend/central_api.py:1682:1: W293 blank line contains whitespace
backend/central_api.py:1685:1: W293 blank line contains whitespace
backend/central_api.py:1694:84: W291 trailing whitespace
backend/central_api.py:1708:1: W293 blank line contains whitespace
backend/central_api.py:1710:1: W293 blank line contains whitespace
backend/central_api.py:1715:1: W293 blank line contains whitespace
backend/central_api.py:1720:1: W293 blank line contains whitespace
backend/central_api.py:1723:1: W293 blank line contains whitespace
backend/central_api.py:1749:1: W293 blank line contains whitespace
backend/central_api.py:1753:1: W293 blank line contains whitespace
backend/central_api.py:1758:1: W293 blank line contains whitespace
backend/central_api.py:1762:1: W293 blank line contains whitespace
backend/central_api.py:1767:1: W293 blank line contains whitespace
backend/central_api.py:1769:1: W293 blank line contains whitespace
backend/central_api.py:1776:1: W293 blank line contains whitespace
backend/central_api.py:1778:1: W293 blank line contains whitespace
backend/central_api.py:1785:1: W293 blank line contains whitespace
backend/central_api.py:1791:1: W293 blank line contains whitespace
backend/central_api.py:1799:1: W293 blank line contains whitespace
backend/central_api.py:1814:1: W293 blank line contains whitespace
backend/central_api.py:1818:1: W293 blank line contains whitespace
backend/central_api.py:1824:1: W293 blank line contains whitespace
backend/central_api.py:1830:1: W293 blank line contains whitespace
backend/central_api.py:1836:1: W293 blank line contains whitespace
backend/central_api.py:1843:1: W293 blank line contains whitespace
backend/central_api.py:1845:1: W293 blank line contains whitespace
backend/central_api.py:1852:1: W293 blank line contains whitespace
backend/central_api.py:1857:1: W293 blank line contains whitespace
backend/central_api.py:1872:1: W293 blank line contains whitespace
backend/central_api.py:1879:1: W293 blank line contains whitespace
backend/central_api.py:1882:1: W293 blank line contains whitespace
backend/central_api.py:1887:1: W293 blank line contains whitespace
backend/central_api.py:1893:1: W293 blank line contains whitespace
backend/central_api.py:1900:1: W293 blank line contains whitespace
backend/central_api.py:1902:1: W293 blank line contains whitespace
backend/central_api.py:1906:1: W293 blank line contains whitespace
backend/central_api.py:1911:1: W293 blank line contains whitespace
backend/central_api.py:1918:1: W293 blank line contains whitespace
backend/central_api.py:1925:1: W293 blank line contains whitespace
backend/central_api.py:1932:1: W293 blank line contains whitespace
backend/central_api.py:1944:1: W293 blank line contains whitespace
backend/central_api.py:1949:1: W293 blank line contains whitespace
backend/central_api.py:1954:1: W293 blank line contains whitespace
backend/central_api.py:1956:1: W293 blank line contains whitespace
backend/central_api.py:1960:1: W293 blank line contains whitespace
backend/central_api.py:1965:1: W293 blank line contains whitespace
backend/central_api.py:1973:1: W293 blank line contains whitespace
backend/central_api.py:1976:1: W293 blank line contains whitespace
backend/central_api.py:1986:1: W293 blank line contains whitespace
backend/central_api.py:1996:1: W293 blank line contains whitespace
backend/central_api.py:2012:1: W293 blank line contains whitespace
backend/central_api.py:2013:72: E713 test for membership should be 'not in'
backend/central_api.py:2019:1: W293 blank line contains whitespace
backend/central_api.py:2026:1: W293 blank line contains whitespace
backend/central_api.py:2043:1: W293 blank line contains whitespace
backend/central_api.py:2051:1: W293 blank line contains whitespace
backend/central_api.py:2058:1: W293 blank line contains whitespace
backend/central_api.py:2063:35: E128 continuation line under-indented for visual indent
backend/central_api.py:2064:35: E128 continuation line under-indented for visual indent
backend/central_api.py:2065:35: E128 continuation line under-indented for visual indent
backend/central_api.py:2066:35: E128 continuation line under-indented for visual indent
backend/central_api.py:2067:1: W293 blank line contains whitespace
backend/central_api.py:2076:1: W293 blank line contains whitespace
backend/central_api.py:2078:28: E128 continuation line under-indented for visual indent
backend/central_api.py:2079:28: E128 continuation line under-indented for visual indent
backend/central_api.py:2080:28: E128 continuation line under-indented for visual indent
backend/central_api.py:2081:1: W293 blank line contains whitespace
backend/central_api.py:2085:1: W293 blank line contains whitespace
backend/central_api.py:2093:1: W293 blank line contains whitespace
backend/central_api.py:2100:1: W293 blank line contains whitespace
backend/central_api.py:2110:1: W293 blank line contains whitespace
backend/central_api.py:2113:1: W293 blank line contains whitespace
backend/central_api.py:2116:1: W293 blank line contains whitespace
backend/central_api.py:2132:1: W293 blank line contains whitespace
backend/central_api.py:2144:1: W293 blank line contains whitespace
backend/central_api.py:2152:1: W293 blank line contains whitespace
backend/central_api.py:2154:1: W293 blank line contains whitespace
backend/central_api.py:2163:1: W293 blank line contains whitespace
backend/central_api.py:2170:1: W293 blank line contains whitespace
backend/central_api.py:2174:1: W293 blank line contains whitespace
backend/central_api.py:2189:1: W293 blank line contains whitespace
backend/central_api.py:2191:1: W293 blank line contains whitespace
backend/central_api.py:2196:1: W293 blank line contains whitespace
backend/central_api.py:2202:1: W293 blank line contains whitespace
backend/central_api.py:2211:1: W293 blank line contains whitespace
backend/central_api.py:2218:1: W293 blank line contains whitespace
backend/central_api.py:2230:1: W293 blank line contains whitespace
backend/central_api.py:2244:1: W293 blank line contains whitespace
backend/central_api.py:2252:1: W293 blank line contains whitespace
backend/central_api.py:2254:1: W293 blank line contains whitespace
backend/central_api.py:2258:1: W293 blank line contains whitespace
backend/central_api.py:2262:1: W293 blank line contains whitespace
backend/central_api.py:2267:1: W293 blank line contains whitespace
backend/central_api.py:2271:1: W293 blank line contains whitespace
backend/central_api.py:2281:1: W293 blank line contains whitespace
backend/central_api.py:2284:1: W293 blank line contains whitespace
backend/central_api.py:2288:1: W293 blank line contains whitespace
backend/central_api.py:2292:1: W293 blank line contains whitespace
backend/central_api.py:2296:1: W293 blank line contains whitespace
backend/central_api.py:2301:1: W293 blank line contains whitespace
backend/central_api.py:2303:1: W293 blank line contains whitespace
backend/central_api.py:2312:1: W293 blank line contains whitespace
backend/central_api.py:2315:1: W293 blank line contains whitespace
backend/central_api.py:2319:1: W293 blank line contains whitespace
backend/central_api.py:2323:1: W293 blank line contains whitespace
backend/central_api.py:2327:1: W293 blank line contains whitespace
backend/central_api.py:2332:1: W293 blank line contains whitespace
backend/central_api.py:2334:1: W293 blank line contains whitespace
backend/central_api.py:2343:1: W293 blank line contains whitespace
backend/central_api.py:2347:1: W293 blank line contains whitespace
backend/central_api.py:2350:1: W293 blank line contains whitespace
backend/central_api.py:2354:1: W293 blank line contains whitespace
backend/central_api.py:2358:1: W293 blank line contains whitespace
backend/central_api.py:2362:1: W293 blank line contains whitespace
backend/central_api.py:2367:1: W293 blank line contains whitespace
backend/central_api.py:2375:1: W293 blank line contains whitespace
backend/central_api.py:2379:1: W293 blank line contains whitespace
backend/central_api.py:2382:1: W293 blank line contains whitespace
backend/central_api.py:2386:1: W293 blank line contains whitespace
backend/central_api.py:2390:1: W293 blank line contains whitespace
backend/central_api.py:2394:1: W293 blank line contains whitespace
backend/central_api.py:2399:1: W293 blank line contains whitespace
backend/central_api.py:2407:1: W293 blank line contains whitespace
backend/central_api.py:2410:1: W293 blank line contains whitespace
backend/central_api.py:2414:1: W293 blank line contains whitespace
backend/central_api.py:2418:1: W293 blank line contains whitespace
backend/central_api.py:2422:1: W293 blank line contains whitespace
backend/central_api.py:2427:1: W293 blank line contains whitespace
backend/central_api.py:2429:1: W293 blank line contains whitespace
backend/central_api.py:2438:1: W293 blank line contains whitespace
backend/central_api.py:2441:1: W293 blank line contains whitespace
backend/central_api.py:2445:1: W293 blank line contains whitespace
backend/central_api.py:2449:1: W293 blank line contains whitespace
backend/central_api.py:2453:1: W293 blank line contains whitespace
backend/central_api.py:2458:1: W293 blank line contains whitespace
backend/central_api.py:2460:1: W293 blank line contains whitespace
backend/central_api.py:2469:1: W293 blank line contains whitespace
backend/central_api.py:2472:1: W293 blank line contains whitespace
backend/central_api.py:2476:1: W293 blank line contains whitespace
backend/central_api.py:2478:1: W293 blank line contains whitespace
backend/central_api.py:2482:1: W293 blank line contains whitespace
backend/central_api.py:2486:1: W293 blank line contains whitespace
backend/central_api.py:2491:1: W293 blank line contains whitespace
backend/central_api.py:2494:1: W293 blank line contains whitespace
backend/central_api.py:2504:1: W293 blank line contains whitespace
backend/central_api.py:2507:1: W293 blank line contains whitespace
backend/central_api.py:2511:1: W293 blank line contains whitespace
backend/central_api.py:2513:1: W293 blank line contains whitespace
backend/central_api.py:2517:1: W293 blank line contains whitespace
backend/central_api.py:2522:1: W293 blank line contains whitespace
backend/central_api.py:2531:1: W293 blank line contains whitespace
backend/central_api.py:2536:1: W293 blank line contains whitespace
backend/central_api.py:2538:1: W293 blank line contains whitespace
backend/central_api.py:2540:1: W293 blank line contains whitespace
backend/central_api.py:2544:1: W293 blank line contains whitespace
backend/central_api.py:2549:1: W293 blank line contains whitespace
backend/central_api.py:2559:1: W293 blank line contains whitespace
backend/central_api.py:2564:1: W293 blank line contains whitespace
backend/central_api.py:2566:1: W293 blank line contains whitespace
backend/central_api.py:2570:1: W293 blank line contains whitespace
backend/central_api.py:2574:1: W293 blank line contains whitespace
backend/central_api.py:2579:1: W293 blank line contains whitespace
backend/central_api.py:2584:1: W293 blank line contains whitespace
backend/central_api.py:2589:1: W293 blank line contains whitespace
backend/central_api.py:2598:1: W293 blank line contains whitespace
backend/central_api.py:2602:1: W293 blank line contains whitespace
backend/central_api.py:2605:1: W293 blank line contains whitespace
backend/central_api.py:2609:1: W293 blank line contains whitespace
backend/central_api.py:2611:1: W293 blank line contains whitespace
backend/central_api.py:2619:1: W293 blank line contains whitespace
backend/central_api.py:2626:1: W293 blank line contains whitespace
backend/central_api.py:2631:1: W293 blank line contains whitespace
backend/central_api.py:2636:1: W293 blank line contains whitespace
backend/central_api.py:2641:1: W293 blank line contains whitespace
backend/central_api.py:2644:1: W293 blank line contains whitespace
backend/central_api.py:2652:1: W293 blank line contains whitespace
backend/central_api.py:2664:1: W293 blank line contains whitespace
backend/central_api.py:2671:1: W293 blank line contains whitespace
backend/central_api.py:2678:1: W293 blank line contains whitespace
backend/central_api.py:2680:1: W293 blank line contains whitespace
backend/central_api.py:2689:1: W293 blank line contains whitespace
backend/central_api.py:2692:1: W293 blank line contains whitespace
backend/central_api.py:2695:1: W293 blank line contains whitespace
backend/central_api.py:2699:1: W293 blank line contains whitespace
backend/central_api.py:2704:1: W293 blank line contains whitespace
backend/central_api.py:2710:1: W293 blank line contains whitespace
backend/central_api.py:2718:1: W293 blank line contains whitespace
backend/central_api.py:2721:1: W293 blank line contains whitespace
backend/central_api.py:2725:1: W293 blank line contains whitespace
backend/central_api.py:2739:1: W293 blank line contains whitespace
backend/central_api.py:2750:1: W293 blank line contains whitespace
backend/central_api.py:2754:1: W293 blank line contains whitespace
backend/central_api.py:2756:1: W293 blank line contains whitespace
backend/central_api.py:2764:1: W293 blank line contains whitespace
backend/central_api.py:2771:1: W293 blank line contains whitespace
backend/central_api.py:2774:1: W293 blank line contains whitespace
backend/central_api.py:2778:1: W293 blank line contains whitespace
backend/central_api.py:2783:1: W293 blank line contains whitespace
backend/central_api.py:2790:1: W293 blank line contains whitespace
backend/central_api.py:2793:1: W293 blank line contains whitespace
backend/central_api.py:2806:1: W293 blank line contains whitespace
backend/central_api.py:2817:1: W293 blank line contains whitespace
backend/central_api.py:2821:1: W293 blank line contains whitespace
backend/central_api.py:2823:1: W293 blank line contains whitespace
backend/central_api.py:2836:1: W293 blank line contains whitespace
backend/central_api.py:2839:1: W293 blank line contains whitespace
backend/central_api.py:2843:1: W293 blank line contains whitespace
backend/central_api.py:2846:1: W293 blank line contains whitespace
backend/central_api.py:2856:1: W293 blank line contains whitespace
backend/central_api.py:2859:1: W293 blank line contains whitespace
backend/central_api.py:2901:1: W293 blank line contains whitespace
backend/central_api.py:2926:1: W293 blank line contains whitespace
backend/central_api.py:2934:1: W293 blank line contains whitespace
backend/central_api.py:2950:1: W293 blank line contains whitespace
backend/central_api.py:2952:1: W293 blank line contains whitespace
backend/central_api.py:2961:1: W293 blank line contains whitespace
backend/central_api.py:2967:1: W293 blank line contains whitespace
backend/central_api.py:2972:1: W293 blank line contains whitespace
backend/central_api.py:2978:1: W293 blank line contains whitespace
backend/central_api.py:2986:1: W293 blank line contains whitespace
backend/central_api.py:2998:1: W293 blank line contains whitespace
backend/central_api.py:3011:1: W293 blank line contains whitespace
backend/central_api.py:3025:1: W293 blank line contains whitespace
backend/central_api.py:3034:1: W293 blank line contains whitespace
backend/central_api.py:3040:1: W293 blank line contains whitespace
backend/central_api.py:3057:1: W293 blank line contains whitespace
backend/central_api.py:3061:1: W293 blank line contains whitespace
backend/central_api.py:3069:1: W293 blank line contains whitespace
backend/central_api.py:3085:1: W293 blank line contains whitespace
backend/central_api.py:3088:1: W293 blank line contains whitespace
backend/central_api.py:3091:1: W293 blank line contains whitespace
backend/central_api.py:3103:1: W293 blank line contains whitespace
backend/central_api.py:3117:1: W293 blank line contains whitespace
backend/central_api.py:3121:1: W293 blank line contains whitespace
backend/central_api.py:3122:5: C901 'CentralAPIHandler.do_PUT' is too complex (40)
backend/central_api.py:3124:1: W293 blank line contains whitespace
backend/central_api.py:3127:1: W293 blank line contains whitespace
backend/central_api.py:3135:1: W293 blank line contains whitespace
backend/central_api.py:3137:1: W293 blank line contains whitespace
backend/central_api.py:3142:1: W293 blank line contains whitespace
backend/central_api.py:3148:1: W293 blank line contains whitespace
backend/central_api.py:3153:1: W293 blank line contains whitespace
backend/central_api.py:3155:1: W293 blank line contains whitespace
backend/central_api.py:3162:1: W293 blank line contains whitespace
backend/central_api.py:3167:1: W293 blank line contains whitespace
backend/central_api.py:3169:1: W293 blank line contains whitespace
backend/central_api.py:3181:1: W293 blank line contains whitespace
backend/central_api.py:3195:1: W293 blank line contains whitespace
backend/central_api.py:3198:1: W293 blank line contains whitespace
backend/central_api.py:3201:1: W293 blank line contains whitespace
backend/central_api.py:3209:1: W293 blank line contains whitespace
backend/central_api.py:3216:1: W293 blank line contains whitespace
backend/central_api.py:3223:1: W293 blank line contains whitespace
backend/central_api.py:3225:1: W293 blank line contains whitespace
backend/central_api.py:3228:1: W293 blank line contains whitespace
backend/central_api.py:3232:1: W293 blank line contains whitespace
backend/central_api.py:3236:1: W293 blank line contains whitespace
backend/central_api.py:3240:1: W293 blank line contains whitespace
backend/central_api.py:3243:1: W293 blank line contains whitespace
backend/central_api.py:3247:1: W293 blank line contains whitespace
backend/central_api.py:3251:1: W293 blank line contains whitespace
backend/central_api.py:3280:1: W293 blank line contains whitespace
backend/central_api.py:3282:1: W293 blank line contains whitespace
backend/central_api.py:3290:1: W293 blank line contains whitespace
backend/central_api.py:3293:1: W293 blank line contains whitespace
backend/central_api.py:3301:1: W293 blank line contains whitespace
backend/central_api.py:3310:1: W293 blank line contains whitespace
backend/central_api.py:3314:1: W293 blank line contains whitespace
backend/central_api.py:3317:1: W293 blank line contains whitespace
backend/central_api.py:3330:1: W293 blank line contains whitespace
backend/central_api.py:3344:1: W293 blank line contains whitespace
backend/central_api.py:3349:1: W293 blank line contains whitespace
backend/central_api.py:3350:5: C901 'CentralAPIHandler.do_DELETE' is too complex (27)
backend/central_api.py:3352:1: W293 blank line contains whitespace
backend/central_api.py:3354:1: W293 blank line contains whitespace
backend/central_api.py:3362:1: W293 blank line contains whitespace
backend/central_api.py:3364:1: W293 blank line contains whitespace
backend/central_api.py:3371:1: W293 blank line contains whitespace
backend/central_api.py:3375:1: W293 blank line contains whitespace
backend/central_api.py:3382:1: W293 blank line contains whitespace
backend/central_api.py:3387:1: W293 blank line contains whitespace
backend/central_api.py:3389:1: W293 blank line contains whitespace
backend/central_api.py:3401:1: W293 blank line contains whitespace
backend/central_api.py:3411:1: W293 blank line contains whitespace
backend/central_api.py:3414:1: W293 blank line contains whitespace
backend/central_api.py:3418:1: W293 blank line contains whitespace
backend/central_api.py:3421:1: W293 blank line contains whitespace
backend/central_api.py:3425:1: W293 blank line contains whitespace
backend/central_api.py:3429:1: W293 blank line contains whitespace
backend/central_api.py:3433:1: W293 blank line contains whitespace
backend/central_api.py:3436:1: W293 blank line contains whitespace
backend/central_api.py:3440:1: W293 blank line contains whitespace
backend/central_api.py:3448:1: W293 blank line contains whitespace
backend/central_api.py:3450:1: W293 blank line contains whitespace
backend/central_api.py:3453:1: W293 blank line contains whitespace
backend/central_api.py:3463:1: W293 blank line contains whitespace
backend/central_api.py:3472:1: W293 blank line contains whitespace
backend/central_api.py:3476:1: W293 blank line contains whitespace
backend/central_api.py:3478:1: W293 blank line contains whitespace
backend/central_api.py:3486:1: W293 blank line contains whitespace
backend/central_api.py:3489:1: W293 blank line contains whitespace
backend/central_api.py:3497:1: W293 blank line contains whitespace
backend/central_api.py:3500:1: W293 blank line contains whitespace
backend/central_api.py:3513:1: W293 blank line contains whitespace
backend/central_api.py:3527:1: W293 blank line contains whitespace
backend/central_api.py:3532:1: W293 blank line contains whitespace
backend/central_api.py:3548:5: F824 `global http_server` is unused: name is never assigned in scope
backend/central_api.py:3549:1: W293 blank line contains whitespace
backend/central_api.py:3552:1: W293 blank line contains whitespace
backend/central_api.py:3558:1: W293 blank line contains whitespace
backend/central_api.py:3568:1: W293 blank line contains whitespace
backend/central_api.py:3582:1: W293 blank line contains whitespace
backend/central_api.py:3589:1: W293 blank line contains whitespace
backend/central_api.py:3596:1: W293 blank line contains whitespace
backend/central_api.py:3601:1: W293 blank line contains whitespace
backend/central_api.py:3604:1: W293 blank line contains whitespace
backend/central_api.py:3614:1: W293 blank line contains whitespace
backend/central_api.py:3617:1: W293 blank line contains whitespace
backend/central_api.py:3620:1: W293 blank line contains whitespace
backend/central_api.py:3623:1: W293 blank line contains whitespace
backend/central_api.py:3626:1: W293 blank line contains whitespace
backend/central_api.py:3630:1: W293 blank line contains whitespace
backend/central_api.py:3640:1: W293 blank line contains whitespace
backend/central_api.py:3642:47: W291 trailing whitespace
backend/central_api.py:3643:27: W291 trailing whitespace
backend/central_api.py:3652:1: W293 blank line contains whitespace
backend/central_api.py:3654:11: F541 f-string is missing placeholders
backend/central_api.py:3655:11: F541 f-string is missing placeholders
backend/central_api.py:3656:11: F541 f-string is missing placeholders
backend/central_api.py:3658:11: F541 f-string is missing placeholders
backend/central_api.py:3664:11: F541 f-string is missing placeholders
backend/central_api.py:3665:11: F541 f-string is missing placeholders
backend/central_api.py:3666:11: F541 f-string is missing placeholders
backend/central_api.py:3667:11: F541 f-string is missing placeholders
backend/central_api.py:3668:11: F541 f-string is missing placeholders
backend/central_api.py:3669:11: F541 f-string is missing placeholders
backend/central_api.py:3670:11: F541 f-string is missing placeholders
backend/central_api.py:3671:11: F541 f-string is missing placeholders
backend/central_api.py:3672:11: F541 f-string is missing placeholders
backend/central_api.py:3673:11: F541 f-string is missing placeholders
backend/central_api.py:3674:11: F541 f-string is missing placeholders
backend/central_api.py:3675:11: F541 f-string is missing placeholders
backend/central_api.py:3676:11: F541 f-string is missing placeholders
backend/central_api.py:3677:11: F541 f-string is missing placeholders
backend/central_api.py:3678:11: F541 f-string is missing placeholders
backend/central_api.py:3679:11: F541 f-string is missing placeholders
backend/central_api.py:3680:11: F541 f-string is missing placeholders
backend/central_api.py:3681:11: F541 f-string is missing placeholders
backend/central_api.py:3682:11: F541 f-string is missing placeholders
backend/central_api.py:3683:11: F541 f-string is missing placeholders
backend/central_api.py:3684:11: F541 f-string is missing placeholders
backend/central_api.py:3685:11: F541 f-string is missing placeholders
backend/central_api.py:3686:11: F541 f-string is missing placeholders
backend/central_api.py:3687:11: F541 f-string is missing placeholders
backend/central_api.py:3688:11: F541 f-string is missing placeholders
backend/central_api.py:3689:11: F541 f-string is missing placeholders
backend/central_api.py:3690:11: F541 f-string is missing placeholders
backend/central_api.py:3691:11: F541 f-string is missing placeholders
backend/central_api.py:3692:11: F541 f-string is missing placeholders
backend/central_api.py:3693:11: F541 f-string is missing placeholders
backend/central_api.py:3694:11: F541 f-string is missing placeholders
backend/central_api.py:3695:11: F541 f-string is missing placeholders
backend/central_api.py:3696:11: F541 f-string is missing placeholders
backend/central_api.py:3697:11: F541 f-string is missing placeholders
backend/central_api.py:3698:11: F541 f-string is missing placeholders
backend/central_api.py:3699:11: F541 f-string is missing placeholders
backend/central_api.py:3700:11: F541 f-string is missing placeholders
backend/central_api.py:3701:11: F541 f-string is missing placeholders
backend/central_api.py:3702:11: F541 f-string is missing placeholders
backend/central_api.py:3703:11: F541 f-string is missing placeholders
backend/central_api.py:3704:11: F541 f-string is missing placeholders
backend/central_api.py:3705:11: F541 f-string is missing placeholders
backend/central_api.py:3706:11: F541 f-string is missing placeholders
backend/central_api.py:3707:11: F541 f-string is missing placeholders
backend/central_api.py:3708:11: F541 f-string is missing placeholders
backend/central_api.py:3709:11: F541 f-string is missing placeholders
backend/central_api.py:3710:11: F541 f-string is missing placeholders
backend/central_api.py:3711:11: F541 f-string is missing placeholders
backend/central_api.py:3712:11: F541 f-string is missing placeholders
backend/central_api.py:3713:11: F541 f-string is missing placeholders
backend/central_api.py:3714:11: F541 f-string is missing placeholders
backend/central_api.py:3715:11: F541 f-string is missing placeholders
backend/central_api.py:3716:11: F541 f-string is missing placeholders
backend/central_api.py:3717:11: F541 f-string is missing placeholders
backend/central_api.py:3718:11: F541 f-string is missing placeholders
backend/central_api.py:3719:1: W293 blank line contains whitespace
backend/crypto_vault.py:10:1: F401 'hashlib' imported but unused
backend/crypto_vault.py:29:1: W293 blank line contains whitespace
backend/crypto_vault.py:38:1: W293 blank line contains whitespace
backend/crypto_vault.py:45:1: W293 blank line contains whitespace
backend/crypto_vault.py:49:1: W293 blank line contains whitespace
backend/crypto_vault.py:52:1: W293 blank line contains whitespace
backend/crypto_vault.py:67:1: W293 blank line contains whitespace
backend/crypto_vault.py:70:1: W293 blank line contains whitespace
backend/crypto_vault.py:73:1: W293 blank line contains whitespace
backend/crypto_vault.py:77:1: W293 blank line contains whitespace
backend/crypto_vault.py:80:1: W293 blank line contains whitespace
backend/crypto_vault.py:92:1: W293 blank line contains whitespace
backend/crypto_vault.py:96:1: W293 blank line contains whitespace
backend/crypto_vault.py:99:1: W293 blank line contains whitespace
backend/crypto_vault.py:105:1: W293 blank line contains whitespace
backend/crypto_vault.py:111:1: W293 blank line contains whitespace
backend/crypto_vault.py:114:1: W293 blank line contains whitespace
backend/crypto_vault.py:118:1: W293 blank line contains whitespace
backend/crypto_vault.py:123:1: W293 blank line contains whitespace
backend/crypto_vault.py:125:1: W293 blank line contains whitespace
backend/crypto_vault.py:129:1: W293 blank line contains whitespace
backend/crypto_vault.py:134:1: W293 blank line contains whitespace
backend/crypto_vault.py:137:1: W293 blank line contains whitespace
backend/crypto_vault.py:143:1: W293 blank line contains whitespace
backend/crypto_vault.py:146:1: W293 blank line contains whitespace
backend/crypto_vault.py:149:1: W293 blank line contains whitespace
backend/crypto_vault.py:153:1: W293 blank line contains whitespace
backend/crypto_vault.py:156:1: W293 blank line contains whitespace
backend/crypto_vault.py:158:9: F841 local variable 'e' is assigned to but never used
backend/crypto_vault.py:161:1: W293 blank line contains whitespace
backend/crypto_vault.py:165:1: W293 blank line contains whitespace
backend/crypto_vault.py:168:1: W293 blank line contains whitespace
backend/crypto_vault.py:178:1: W293 blank line contains whitespace
backend/crypto_vault.py:182:1: W293 blank line contains whitespace
backend/crypto_vault.py:187:1: W293 blank line contains whitespace
backend/crypto_vault.py:200:1: W293 blank line contains whitespace
backend/crypto_vault.py:203:1: W293 blank line contains whitespace
backend/crypto_vault.py:214:1: W293 blank line contains whitespace
backend/crypto_vault.py:218:1: W293 blank line contains whitespace
backend/crypto_vault.py:224:1: W293 blank line contains whitespace
backend/crypto_vault.py:231:1: W293 blank line contains whitespace
backend/crypto_vault.py:236:1: W293 blank line contains whitespace
backend/crypto_vault.py:240:1: W293 blank line contains whitespace
backend/crypto_vault.py:249:1: W293 blank line contains whitespace
backend/crypto_vault.py:259:1: W293 blank line contains whitespace
backend/database.py:26:1: F811 redefinition of unused 'Path' from line 15
backend/database.py:43:1: E302 expected 2 blank lines, found 1
backend/database.py:47:1: E302 expected 2 blank lines, found 1
backend/database.py:51:1: E302 expected 2 blank lines, found 1
backend/database.py:61:1: E302 expected 2 blank lines, found 1
backend/database.py:72:5: E722 do not use bare 'except'
backend/database.py:75:1: E302 expected 2 blank lines, found 1
backend/database.py:79:1: E302 expected 2 blank lines, found 1
backend/database.py:83:1: W293 blank line contains whitespace
backend/database.py:86:1: W293 blank line contains whitespace
backend/database.py:109:1: W293 blank line contains whitespace
backend/database.py:123:1: W293 blank line contains whitespace
backend/database.py:135:1: W293 blank line contains whitespace
backend/database.py:147:1: W293 blank line contains whitespace
backend/database.py:161:1: W293 blank line contains whitespace
backend/database.py:177:1: W293 blank line contains whitespace
backend/database.py:196:1: W293 blank line contains whitespace
backend/database.py:214:1: W293 blank line contains whitespace
backend/database.py:227:1: W293 blank line contains whitespace
backend/database.py:242:1: W293 blank line contains whitespace
backend/database.py:245:64: W291 trailing whitespace
backend/database.py:248:1: W293 blank line contains whitespace
backend/database.py:250:61: W291 trailing whitespace
backend/database.py:253:1: W293 blank line contains whitespace
backend/database.py:267:1: W293 blank line contains whitespace
backend/database.py:284:1: W293 blank line contains whitespace
backend/database.py:300:1: W293 blank line contains whitespace
backend/database.py:303:58: W291 trailing whitespace
backend/database.py:306:1: W293 blank line contains whitespace
backend/database.py:308:57: W291 trailing whitespace
backend/database.py:311:1: W293 blank line contains whitespace
backend/database.py:313:61: W291 trailing whitespace
backend/database.py:316:1: W293 blank line contains whitespace
backend/database.py:326:1: W293 blank line contains whitespace
backend/database.py:336:1: W293 blank line contains whitespace
backend/database.py:339:69: W291 trailing whitespace
backend/database.py:342:1: W293 blank line contains whitespace
backend/database.py:344:72: W291 trailing whitespace
backend/database.py:347:1: W293 blank line contains whitespace
backend/database.py:368:1: W293 blank line contains whitespace
backend/database.py:371:55: W291 trailing whitespace
backend/database.py:374:1: W293 blank line contains whitespace
backend/database.py:376:53: W291 trailing whitespace
backend/database.py:379:1: W293 blank line contains whitespace
backend/database.py:381:52: W291 trailing whitespace
backend/database.py:384:1: W293 blank line contains whitespace
backend/database.py:386:56: W291 trailing whitespace
backend/database.py:389:1: W293 blank line contains whitespace
backend/database.py:408:1: W293 blank line contains whitespace
backend/database.py:411:56: W291 trailing whitespace
backend/database.py:414:1: W293 blank line contains whitespace
backend/database.py:431:1: W293 blank line contains whitespace
backend/database.py:434:69: W291 trailing whitespace
backend/database.py:437:1: W293 blank line contains whitespace
backend/database.py:439:71: W291 trailing whitespace
backend/database.py:442:1: W293 blank line contains whitespace
backend/database.py:446:1: E302 expected 2 blank lines, found 1
backend/database.py:453:1: E302 expected 2 blank lines, found 1
backend/database.py:457:1: W293 blank line contains whitespace
backend/database.py:462:1: W293 blank line contains whitespace
backend/database.py:467:1: W293 blank line contains whitespace
backend/database.py:471:1: W293 blank line contains whitespace
backend/database.py:473:1: W293 blank line contains whitespace
backend/database.py:477:1: W293 blank line contains whitespace
backend/database.py:482:1: E302 expected 2 blank lines, found 1
backend/database.py:486:1: W293 blank line contains whitespace
backend/database.py:491:1: W293 blank line contains whitespace
backend/database.py:494:1: W293 blank line contains whitespace
backend/database.py:498:1: W293 blank line contains whitespace
backend/database.py:502:1: E302 expected 2 blank lines, found 1
backend/database.py:506:1: W293 blank line contains whitespace
backend/database.py:509:1: W293 blank line contains whitespace
backend/database.py:513:1: W293 blank line contains whitespace
backend/database.py:516:1: W293 blank line contains whitespace
backend/database.py:520:1: W293 blank line contains whitespace
backend/database.py:524:1: E302 expected 2 blank lines, found 1
backend/database.py:528:1: W293 blank line contains whitespace
backend/database.py:529:151: E501 line too long (155 > 150 characters)
backend/database.py:530:1: W293 blank line contains whitespace
backend/database.py:533:1: W293 blank line contains whitespace
backend/database.py:541:1: W293 blank line contains whitespace
backend/database.py:545:1: W293 blank line contains whitespace
backend/database.py:548:1: W293 blank line contains whitespace
backend/database.py:550:1: W293 blank line contains whitespace
backend/database.py:555:1: W293 blank line contains whitespace
backend/database.py:557:1: W293 blank line contains whitespace
backend/database.py:562:1: E302 expected 2 blank lines, found 1
backend/database.py:566:1: W293 blank line contains whitespace
backend/database.py:569:1: W293 blank line contains whitespace
backend/database.py:573:1: W293 blank line contains whitespace
backend/database.py:576:1: W293 blank line contains whitespace
backend/database.py:578:1: W293 blank line contains whitespace
backend/database.py:583:1: E302 expected 2 blank lines, found 1
backend/database.py:587:1: W293 blank line contains whitespace
backend/database.py:590:1: W293 blank line contains whitespace
backend/database.py:592:23: W291 trailing whitespace
backend/database.py:593:70: W291 trailing whitespace
backend/database.py:596:1: W293 blank line contains whitespace
backend/database.py:602:1: E302 expected 2 blank lines, found 1
backend/database.py:606:1: W293 blank line contains whitespace
backend/database.py:610:1: W293 blank line contains whitespace
backend/database.py:615:1: W293 blank line contains whitespace
backend/database.py:619:1: E302 expected 2 blank lines, found 1
backend/database.py:623:1: W293 blank line contains whitespace
backend/database.py:626:45: W291 trailing whitespace
backend/database.py:633:45: W291 trailing whitespace
backend/database.py:638:1: W293 blank line contains whitespace
backend/database.py:641:1: W293 blank line contains whitespace
backend/database.py:647:9: E722 do not use bare 'except'
backend/database.py:650:1: W293 blank line contains whitespace
backend/database.py:654:1: E302 expected 2 blank lines, found 1
backend/database.py:658:1: W293 blank line contains whitespace
backend/database.py:660:39: W291 trailing whitespace
backend/database.py:663:1: W293 blank line contains whitespace
backend/database.py:667:1: W293 blank line contains whitespace
backend/database.py:672:1: E302 expected 2 blank lines, found 1
backend/database.py:676:1: W293 blank line contains whitespace
backend/database.py:681:1: W293 blank line contains whitespace
backend/database.py:685:1: W293 blank line contains whitespace
backend/database.py:688:1: E302 expected 2 blank lines, found 1
backend/database.py:692:1: W293 blank line contains whitespace
backend/database.py:695:1: W293 blank line contains whitespace
backend/database.py:699:1: W293 blank line contains whitespace
backend/database.py:703:1: W293 blank line contains whitespace
backend/database.py:706:1: W293 blank line contains whitespace
backend/database.py:708:1: W293 blank line contains whitespace
backend/database.py:711:1: W293 blank line contains whitespace
backend/database.py:715:1: W293 blank line contains whitespace
backend/database.py:719:1: E302 expected 2 blank lines, found 1
backend/database.py:723:1: W293 blank line contains whitespace
backend/database.py:725:1: W293 blank line contains whitespace
backend/database.py:731:1: E302 expected 2 blank lines, found 1
backend/database.py:735:1: W293 blank line contains whitespace
backend/database.py:738:1: W293 blank line contains whitespace
backend/database.py:741:1: W293 blank line contains whitespace
backend/database.py:744:1: W293 blank line contains whitespace
backend/database.py:747:1: W293 blank line contains whitespace
backend/database.py:749:1: W293 blank line contains whitespace
backend/database.py:760:1: E302 expected 2 blank lines, found 1
backend/database.py:764:1: W293 blank line contains whitespace
backend/database.py:767:1: W293 blank line contains whitespace
backend/database.py:772:1: W293 blank line contains whitespace
backend/database.py:776:1: W293 blank line contains whitespace
backend/database.py:778:1: W293 blank line contains whitespace
backend/database.py:782:1: W293 blank line contains whitespace
backend/database.py:787:1: E302 expected 2 blank lines, found 1
backend/database.py:791:1: W293 blank line contains whitespace
backend/database.py:794:1: W293 blank line contains whitespace
backend/database.py:798:1: W293 blank line contains whitespace
backend/database.py:800:1: W293 blank line contains whitespace
backend/database.py:804:1: W293 blank line contains whitespace
backend/database.py:808:1: W293 blank line contains whitespace
backend/database.py:813:1: W293 blank line contains whitespace
backend/database.py:818:1: W293 blank line contains whitespace
backend/database.py:821:27: W291 trailing whitespace
backend/database.py:822:43: W291 trailing whitespace
backend/database.py:825:1: W293 blank line contains whitespace
backend/database.py:828:1: W293 blank line contains whitespace
backend/database.py:836:1: E302 expected 2 blank lines, found 1
backend/database.py:840:1: W293 blank line contains whitespace
backend/database.py:847:1: W293 blank line contains whitespace
backend/database.py:850:1: W293 blank line contains whitespace
backend/database.py:853:1: W293 blank line contains whitespace
backend/database.py:855:1: W293 blank line contains whitespace
backend/database.py:859:1: W293 blank line contains whitespace
backend/database.py:867:1: E302 expected 2 blank lines, found 1
backend/database.py:871:1: W293 blank line contains whitespace
backend/database.py:874:1: W293 blank line contains whitespace
backend/database.py:877:1: W293 blank line contains whitespace
backend/database.py:880:1: E302 expected 2 blank lines, found 1
backend/database.py:884:1: W293 blank line contains whitespace
backend/database.py:886:76: W291 trailing whitespace
backend/database.py:887:25: W291 trailing whitespace
backend/database.py:890:1: W293 blank line contains whitespace
backend/database.py:893:1: W293 blank line contains whitespace
backend/database.py:896:1: W293 blank line contains whitespace
backend/database.py:901:1: E302 expected 2 blank lines, found 1
backend/database.py:905:1: W293 blank line contains whitespace
backend/database.py:907:76: W291 trailing whitespace
backend/database.py:908:25: W291 trailing whitespace
backend/database.py:911:1: W293 blank line contains whitespace
backend/database.py:914:1: W293 blank line contains whitespace
backend/database.py:918:1: W293 blank line contains whitespace
backend/database.py:922:1: E302 expected 2 blank lines, found 1
backend/database.py:926:1: W293 blank line contains whitespace
backend/database.py:929:1: W293 blank line contains whitespace
backend/database.py:933:1: W293 blank line contains whitespace
backend/database.py:935:1: W293 blank line contains whitespace
backend/database.py:939:1: W293 blank line contains whitespace
backend/database.py:941:1: W293 blank line contains whitespace
backend/database.py:943:27: W291 trailing whitespace
backend/database.py:944:30: W291 trailing whitespace
backend/database.py:947:1: W293 blank line contains whitespace
backend/database.py:950:1: W293 blank line contains whitespace
backend/database.py:953:1: E302 expected 2 blank lines, found 1
backend/database.py:957:1: W293 blank line contains whitespace
backend/database.py:959:29: W291 trailing whitespace
backend/database.py:962:1: W293 blank line contains whitespace
backend/database.py:966:1: W293 blank line contains whitespace
backend/database.py:971:1: E302 expected 2 blank lines, found 1
backend/database.py:975:1: W293 blank line contains whitespace
backend/database.py:981:1: W293 blank line contains whitespace
backend/database.py:985:1: W293 blank line contains whitespace
backend/database.py:987:1: W293 blank line contains whitespace
backend/database.py:992:1: E302 expected 2 blank lines, found 1
backend/database.py:996:1: W293 blank line contains whitespace
backend/database.py:1001:1: W293 blank line contains whitespace
backend/database.py:1004:1: W293 blank line contains whitespace
backend/database.py:1008:1: W293 blank line contains whitespace
backend/database.py:1012:1: E302 expected 2 blank lines, found 1
backend/database.py:1016:1: W293 blank line contains whitespace
backend/database.py:1019:1: W293 blank line contains whitespace
backend/database.py:1023:1: W293 blank line contains whitespace
backend/database.py:1026:1: W293 blank line contains whitespace
backend/database.py:1030:1: E302 expected 2 blank lines, found 1
backend/database.py:1034:1: W293 blank line contains whitespace
backend/database.py:1036:1: W293 blank line contains whitespace
backend/database.py:1039:1: W293 blank line contains whitespace
backend/database.py:1044:1: W293 blank line contains whitespace
backend/database.py:1048:1: W293 blank line contains whitespace
backend/database.py:1051:1: W293 blank line contains whitespace
backend/database.py:1053:1: W293 blank line contains whitespace
backend/database.py:1058:1: W293 blank line contains whitespace
backend/database.py:1060:1: W293 blank line contains whitespace
backend/database.py:1065:1: E302 expected 2 blank lines, found 1
backend/database.py:1069:1: W293 blank line contains whitespace
backend/database.py:1072:1: W293 blank line contains whitespace
backend/database.py:1076:1: W293 blank line contains whitespace
backend/database.py:1079:1: W293 blank line contains whitespace
backend/database.py:1081:1: W293 blank line contains whitespace
backend/database.py:1088:1: E302 expected 2 blank lines, found 1
backend/database.py:1092:1: W293 blank line contains whitespace
backend/database.py:1097:1: W293 blank line contains whitespace
backend/database.py:1105:13: E722 do not use bare 'except'
backend/database.py:1107:1: W293 blank line contains whitespace
backend/database.py:1112:1: W293 blank line contains whitespace
backend/database.py:1116:1: W293 blank line contains whitespace
backend/database.py:1118:1: W293 blank line contains whitespace
backend/database.py:1122:1: W293 blank line contains whitespace
backend/database.py:1127:1: E302 expected 2 blank lines, found 1
backend/database.py:1131:1: W293 blank line contains whitespace
backend/database.py:1133:91: W291 trailing whitespace
backend/database.py:1135:22: W291 trailing whitespace
backend/database.py:1138:1: W293 blank line contains whitespace
backend/database.py:1141:1: W293 blank line contains whitespace
backend/database.py:1145:1: W293 blank line contains whitespace
backend/database.py:1149:1: E302 expected 2 blank lines, found 1
backend/database.py:1153:1: W293 blank line contains whitespace
backend/database.py:1156:1: W293 blank line contains whitespace
backend/database.py:1160:1: W293 blank line contains whitespace
backend/database.py:1163:1: W293 blank line contains whitespace
backend/database.py:1167:1: W293 blank line contains whitespace
backend/database.py:1171:1: E302 expected 2 blank lines, found 1
backend/database.py:1175:1: W293 blank line contains whitespace
backend/database.py:1177:1: W293 blank line contains whitespace
backend/database.py:1180:1: W293 blank line contains whitespace
backend/database.py:1188:1: W293 blank line contains whitespace
backend/database.py:1192:1: W293 blank line contains whitespace
backend/database.py:1195:1: W293 blank line contains whitespace
backend/database.py:1197:1: W293 blank line contains whitespace
backend/database.py:1202:1: W293 blank line contains whitespace
backend/database.py:1204:1: W293 blank line contains whitespace
backend/database.py:1209:1: E302 expected 2 blank lines, found 1
backend/database.py:1213:1: W293 blank line contains whitespace
backend/database.py:1216:1: W293 blank line contains whitespace
backend/database.py:1220:1: W293 blank line contains whitespace
backend/database.py:1223:1: W293 blank line contains whitespace
backend/database.py:1225:1: W293 blank line contains whitespace
backend/database.py:1230:1: E302 expected 2 blank lines, found 1
backend/database.py:1234:1: W293 blank line contains whitespace
backend/database.py:1236:24: W291 trailing whitespace
backend/database.py:1237:42: W291 trailing whitespace
backend/database.py:1240:1: W293 blank line contains whitespace
backend/database.py:1244:1: E302 expected 2 blank lines, found 1
backend/database.py:1248:1: W293 blank line contains whitespace
backend/database.py:1251:1: W293 blank line contains whitespace
backend/database.py:1255:1: W293 blank line contains whitespace
backend/database.py:1258:1: W293 blank line contains whitespace
backend/database.py:1264:1: E302 expected 2 blank lines, found 1
backend/database.py:1268:1: W293 blank line contains whitespace
backend/database.py:1270:1: W293 blank line contains whitespace
backend/database.py:1273:1: W293 blank line contains whitespace
backend/database.py:1276:1: W293 blank line contains whitespace
backend/database.py:1292:1: W293 blank line contains whitespace
backend/database.py:1295:1: E302 expected 2 blank lines, found 1
backend/database.py:1299:1: W293 blank line contains whitespace
backend/database.py:1301:1: W293 blank line contains whitespace
backend/database.py:1304:1: W293 blank line contains whitespace
backend/database.py:1307:1: W293 blank line contains whitespace
backend/database.py:1314:13: E722 do not use bare 'except'
backend/database.py:1316:1: W293 blank line contains whitespace
backend/database.py:1327:1: W293 blank line contains whitespace
backend/database.py:1330:1: E302 expected 2 blank lines, found 1
backend/database.py:1335:1: E302 expected 2 blank lines, found 1
backend/database.py:1340:1: E302 expected 2 blank lines, found 1
backend/database.py:1344:1: W293 blank line contains whitespace
backend/database.py:1346:1: W293 blank line contains whitespace
backend/database.py:1349:1: W293 blank line contains whitespace
backend/database.py:1352:1: W293 blank line contains whitespace
backend/database.py:1364:1: W293 blank line contains whitespace
backend/database.py:1367:1: E302 expected 2 blank lines, found 1
backend/database.py:1371:1: W293 blank line contains whitespace
backend/database.py:1374:1: W293 blank line contains whitespace
backend/database.py:1380:1: W293 blank line contains whitespace
backend/database.py:1382:1: W293 blank line contains whitespace
backend/database.py:1389:1: W293 blank line contains whitespace
backend/database.py:1392:1: E302 expected 2 blank lines, found 1
backend/database.py:1395:1: W293 blank line contains whitespace
backend/database.py:1403:1: W293 blank line contains whitespace
backend/database.py:1409:1: W293 blank line contains whitespace
backend/database.py:1420:1: W293 blank line contains whitespace
backend/database.py:1423:1: W293 blank line contains whitespace
backend/database.py:1426:1: W293 blank line contains whitespace
backend/database.py:1428:80: W291 trailing whitespace
backend/database.py:1440:1: W293 blank line contains whitespace
backend/database.py:1443:1: E302 expected 2 blank lines, found 1
backend/database.py:1446:1: W293 blank line contains whitespace
backend/database.py:1454:1: W293 blank line contains whitespace
backend/database.py:1468:1: W293 blank line contains whitespace
backend/database.py:1481:1: W293 blank line contains whitespace
backend/database.py:1490:1: W293 blank line contains whitespace
backend/database.py:1492:1: W293 blank line contains whitespace
backend/database.py:1497:1: E302 expected 2 blank lines, found 1
backend/database.py:1501:1: W293 blank line contains whitespace
backend/database.py:1508:1: W293 blank line contains whitespace
backend/database.py:1517:1: E302 expected 2 blank lines, found 1
backend/database.py:1522:1: W293 blank line contains whitespace
backend/database.py:1525:39: W291 trailing whitespace
backend/database.py:1531:39: W291 trailing whitespace
backend/database.py:1535:1: W293 blank line contains whitespace
backend/database.py:1540:1: E302 expected 2 blank lines, found 1
backend/database.py:1545:1: W293 blank line contains whitespace
backend/database.py:1551:1: E302 expected 2 blank lines, found 1
backend/database.py:1555:1: W293 blank line contains whitespace
backend/database.py:1558:1: W293 blank line contains whitespace
backend/database.py:1562:1: W293 blank line contains whitespace
backend/database.py:1566:1: W293 blank line contains whitespace
backend/database.py:1570:1: W293 blank line contains whitespace
backend/database.py:1574:1: W293 blank line contains whitespace
backend/database.py:1577:1: W293 blank line contains whitespace
backend/database.py:1580:32: W291 trailing whitespace
backend/database.py:1584:1: W293 blank line contains whitespace
backend/database.py:1592:1: E302 expected 2 blank lines, found 1
backend/database.py:1596:1: W293 blank line contains whitespace
backend/database.py:1600:36: W291 trailing whitespace
backend/database.py:1601:51: W291 trailing whitespace
backend/database.py:1615:1: E302 expected 2 blank lines, found 1
backend/database.py:1619:1: W293 blank line contains whitespace
backend/database.py:1622:1: W293 blank line contains whitespace
backend/database.py:1640:1: E302 expected 2 blank lines, found 1
backend/database.py:1644:1: W293 blank line contains whitespace
backend/database.py:1649:1: W293 blank line contains whitespace
backend/database.py:1653:39: W291 trailing whitespace
backend/database.py:1654:68: W291 trailing whitespace
backend/database.py:1662:44: W291 trailing whitespace
backend/database.py:1666:1: W293 blank line contains whitespace
backend/database.py:1676:1: E302 expected 2 blank lines, found 1
backend/database.py:1679:1: W293 blank line contains whitespace
backend/database.py:1688:1: W293 blank line contains whitespace
backend/database.py:1695:1: W293 blank line contains whitespace
backend/database.py:1700:1: W293 blank line contains whitespace
backend/database.py:1705:1: W293 blank line contains whitespace
backend/database.py:1713:1: E302 expected 2 blank lines, found 1
backend/database.py:1716:1: W293 blank line contains whitespace
backend/database.py:1725:1: W293 blank line contains whitespace
backend/database.py:1731:1: W293 blank line contains whitespace
backend/database.py:1735:1: W293 blank line contains whitespace
backend/database.py:1739:1: W293 blank line contains whitespace
backend/database.py:1743:1: W293 blank line contains whitespace
backend/database.py:1747:1: W293 blank line contains whitespace
backend/database.py:1751:1: W293 blank line contains whitespace
backend/database.py:1755:1: W293 blank line contains whitespace
backend/database.py:1758:1: W293 blank line contains whitespace
backend/database.py:1760:1: W293 blank line contains whitespace
backend/database.py:1775:1: W293 blank line contains whitespace
backend/database.py:1779:1: E302 expected 2 blank lines, found 1
backend/database.py:1782:1: W293 blank line contains whitespace
backend/database.py:1785:1: W293 blank line contains whitespace
backend/database.py:1791:1: W293 blank line contains whitespace
backend/database.py:1795:1: W293 blank line contains whitespace
backend/database.py:1798:31: W291 trailing whitespace
backend/database.py:1801:1: W293 blank line contains whitespace
backend/database.py:1805:1: W293 blank line contains whitespace
backend/database.py:1810:1: E302 expected 2 blank lines, found 1
backend/database.py:1813:1: W293 blank line contains whitespace
backend/database.py:1818:1: W293 blank line contains whitespace
backend/database.py:1825:1: W293 blank line contains whitespace
backend/database.py:1829:1: W293 blank line contains whitespace
backend/database.py:1834:1: W293 blank line contains whitespace
backend/database.py:1842:1: E302 expected 2 blank lines, found 1
backend/database.py:1845:1: W293 blank line contains whitespace
backend/database.py:1849:1: W293 blank line contains whitespace
backend/database.py:1855:1: W293 blank line contains whitespace
backend/database.py:1858:1: W293 blank line contains whitespace
backend/database.py:1860:37: W291 trailing whitespace
backend/database.py:1864:1: W293 blank line contains whitespace
backend/database.py:1872:1: E302 expected 2 blank lines, found 1
backend/database.py:1875:1: W293 blank line contains whitespace
backend/database.py:1878:1: W293 blank line contains whitespace
backend/database.py:1884:1: W293 blank line contains whitespace
backend/database.py:1887:1: W293 blank line contains whitespace
backend/database.py:1889:37: W291 trailing whitespace
backend/database.py:1893:1: W293 blank line contains whitespace
backend/database.py:1901:1: E302 expected 2 blank lines, found 1
backend/database.py:1904:1: W293 blank line contains whitespace
backend/database.py:1909:1: W293 blank line contains whitespace
backend/database.py:1915:1: W293 blank line contains whitespace
backend/database.py:1918:1: W293 blank line contains whitespace
backend/database.py:1922:1: W293 blank line contains whitespace
backend/database.py:1926:1: W293 blank line contains whitespace
backend/database.py:1930:1: W293 blank line contains whitespace
backend/database.py:1932:1: W293 blank line contains whitespace
backend/database.py:1934:1: W293 blank line contains whitespace
backend/database.py:1948:1: W293 blank line contains whitespace
backend/database.py:1954:1: E302 expected 2 blank lines, found 1
backend/database.py:1957:1: W293 blank line contains whitespace
backend/database.py:1962:1: W293 blank line contains whitespace
backend/database.py:1967:1: W293 blank line contains whitespace
backend/database.py:1970:1: W293 blank line contains whitespace
backend/database.py:1973:1: W293 blank line contains whitespace
backend/database.py:1979:1: W293 blank line contains whitespace
backend/database.py:1987:1: W293 blank line contains whitespace
backend/database.py:1995:1: E302 expected 2 blank lines, found 1
backend/database.py:1998:1: W293 blank line contains whitespace
backend/database.py:2001:1: W293 blank line contains whitespace
backend/database.py:2007:1: W293 blank line contains whitespace
backend/database.py:2013:1: W293 blank line contains whitespace
backend/database.py:2016:1: W293 blank line contains whitespace
backend/database.py:2025:1: E302 expected 2 blank lines, found 1
backend/database.py:2028:1: W293 blank line contains whitespace
backend/database.py:2032:1: W293 blank line contains whitespace
backend/database.py:2038:1: W293 blank line contains whitespace
backend/database.py:2046:1: W293 blank line contains whitespace
backend/database.py:2055:1: W293 blank line contains whitespace
backend/database.py:2061:1: E302 expected 2 blank lines, found 1
backend/database.py:2064:1: W293 blank line contains whitespace
backend/database.py:2071:1: W293 blank line contains whitespace
backend/database.py:2078:1: W293 blank line contains whitespace
backend/database.py:2082:1: W293 blank line contains whitespace
backend/database.py:2087:1: W293 blank line contains whitespace
backend/database.py:2095:1: E302 expected 2 blank lines, found 1
backend/database.py:2098:1: W293 blank line contains whitespace
backend/database.py:2101:1: W293 blank line contains whitespace
backend/database.py:2107:1: W293 blank line contains whitespace
backend/database.py:2110:1: W293 blank line contains whitespace
backend/database.py:2114:1: W293 blank line contains whitespace
backend/database.py:2117:1: W293 blank line contains whitespace
backend/database.py:2121:1: E302 expected 2 blank lines, found 1
backend/database.py:2124:1: W293 blank line contains whitespace
backend/database.py:2133:1: W293 blank line contains whitespace
backend/database.py:2139:1: W293 blank line contains whitespace
backend/database.py:2143:1: W293 blank line contains whitespace
backend/database.py:2147:1: W293 blank line contains whitespace
backend/database.py:2151:1: W293 blank line contains whitespace
backend/database.py:2155:1: W293 blank line contains whitespace
backend/database.py:2159:1: W293 blank line contains whitespace
backend/database.py:2163:1: W293 blank line contains whitespace
backend/database.py:2166:1: W293 blank line contains whitespace
backend/database.py:2168:1: W293 blank line contains whitespace
backend/database.py:2171:1: W293 blank line contains whitespace
backend/database.py:2175:1: W293 blank line contains whitespace
backend/database.py:2179:1: E302 expected 2 blank lines, found 1
backend/database.py:2182:1: W293 blank line contains whitespace
backend/database.py:2191:1: W293 blank line contains whitespace
backend/database.py:2197:1: W293 blank line contains whitespace
backend/database.py:2201:1: W293 blank line contains whitespace
backend/database.py:2205:1: W293 blank line contains whitespace
backend/database.py:2209:1: W293 blank line contains whitespace
backend/database.py:2213:1: W293 blank line contains whitespace
backend/database.py:2217:1: W293 blank line contains whitespace
backend/database.py:2221:1: W293 blank line contains whitespace
backend/database.py:2223:1: W293 blank line contains whitespace
backend/database.py:2226:1: W293 blank line contains whitespace
backend/database.py:2234:1: E302 expected 2 blank lines, found 1
backend/database.py:2237:1: W293 blank line contains whitespace
backend/database.py:2240:1: W293 blank line contains whitespace
backend/database.py:2246:1: W293 blank line contains whitespace
backend/database.py:2248:26: W291 trailing whitespace
backend/database.py:2251:1: W293 blank line contains whitespace
backend/database.py:2255:1: W293 blank line contains whitespace
backend/database.py:2260:1: E302 expected 2 blank lines, found 1
backend/database.py:2263:1: W293 blank line contains whitespace
backend/database.py:2269:1: W293 blank line contains whitespace
backend/database.py:2275:1: W293 blank line contains whitespace
backend/database.py:2281:1: W293 blank line contains whitespace
backend/database.py:2293:1: E302 expected 2 blank lines, found 1
backend/database.py:2296:1: W293 blank line contains whitespace
backend/database.py:2302:1: W293 blank line contains whitespace
backend/database.py:2304:1: W293 blank line contains whitespace
backend/database.py:2307:1: W293 blank line contains whitespace
backend/database.py:2311:1: W293 blank line contains whitespace
backend/database.py:2315:1: E302 expected 2 blank lines, found 1
backend/database.py:2318:1: W293 blank line contains whitespace
backend/database.py:2321:1: W293 blank line contains whitespace
backend/database.py:2327:1: W293 blank line contains whitespace
backend/database.py:2330:1: W293 blank line contains whitespace
backend/database.py:2334:1: W293 blank line contains whitespace
backend/database.py:2337:1: W293 blank line contains whitespace
backend/database.py:2341:1: E302 expected 2 blank lines, found 1
backend/database.py:2344:1: W293 blank line contains whitespace
backend/database.py:2348:1: W293 blank line contains whitespace
backend/database.py:2354:1: W293 blank line contains whitespace
backend/database.py:2356:1: W293 blank line contains whitespace
backend/database.py:2359:1: W293 blank line contains whitespace
backend/database.py:2364:1: W293 blank line contains whitespace
backend/database.py:2368:1: W293 blank line contains whitespace
backend/database.py:2370:1: W293 blank line contains whitespace
backend/database.py:2372:1: W293 blank line contains whitespace
backend/database.py:2377:1: W293 blank line contains whitespace
backend/database.py:2379:1: W293 blank line contains whitespace
backend/database.py:2384:1: E302 expected 2 blank lines, found 1
backend/database.py:2387:1: W293 blank line contains whitespace
backend/database.py:2390:1: W293 blank line contains whitespace
backend/database.py:2396:1: W293 blank line contains whitespace
backend/database.py:2399:1: W293 blank line contains whitespace
backend/database.py:2403:1: W293 blank line contains whitespace
backend/database.py:2406:1: W293 blank line contains whitespace
backend/database.py:2408:1: W293 blank line contains whitespace
backend/database.py:2413:1: E302 expected 2 blank lines, found 1
backend/database.py:2416:1: W293 blank line contains whitespace
backend/database.py:2421:1: W293 blank line contains whitespace
backend/database.py:2427:1: W293 blank line contains whitespace
backend/database.py:2433:1: W293 blank line contains whitespace
backend/database.py:2444:1: E302 expected 2 blank lines, found 1
backend/database.py:2447:1: W293 blank line contains whitespace
backend/database.py:2451:1: W293 blank line contains whitespace
backend/database.py:2457:1: W293 blank line contains whitespace
backend/database.py:2460:39: W291 trailing whitespace
backend/database.py:2463:1: W293 blank line contains whitespace
backend/database.py:2467:1: W293 blank line contains whitespace
backend/database.py:2470:1: W293 blank line contains whitespace
backend/database.py:2472:1: W293 blank line contains whitespace
backend/database.py:2477:1: E302 expected 2 blank lines, found 1
backend/database.py:2480:1: W293 blank line contains whitespace
backend/database.py:2483:1: W293 blank line contains whitespace
backend/database.py:2489:1: W293 blank line contains whitespace
backend/database.py:2496:1: W293 blank line contains whitespace
backend/database.py:2499:1: W293 blank line contains whitespace
backend/database.py:2503:1: W293 blank line contains whitespace
backend/database.py:2507:1: E302 expected 2 blank lines, found 1
backend/database.py:2510:1: W293 blank line contains whitespace
backend/database.py:2513:1: W293 blank line contains whitespace
backend/database.py:2519:1: W293 blank line contains whitespace
backend/database.py:2524:1: W293 blank line contains whitespace
backend/database.py:2526:1: W293 blank line contains whitespace
backend/database.py:2533:75: W291 trailing whitespace
backend/database.py:2537:1: W293 blank line contains whitespace
backend/database.py:2547:1: W293 blank line contains whitespace
backend/database.py:2554:1: W293 blank line contains whitespace
backend/database.py:2558:1: W293 blank line contains whitespace
backend/database.py:2561:1: W293 blank line contains whitespace
backend/database.py:2564:61: W291 trailing whitespace
backend/database.py:2570:1: W293 blank line contains whitespace
backend/database.py:2582:1: W293 blank line contains whitespace
backend/database.py:2585:1: W293 blank line contains whitespace
backend/database.py:2591:1: W293 blank line contains whitespace
backend/database.py:2596:1: W293 blank line contains whitespace
backend/database.py:2599:1: W293 blank line contains whitespace
backend/database.py:2606:13: E722 do not use bare 'except'
backend/database.py:2611:1: W293 blank line contains whitespace
backend/database.py:2619:1: W293 blank line contains whitespace
backend/database.py:2622:1: W293 blank line contains whitespace
backend/database.py:2628:1: W293 blank line contains whitespace
backend/database.py:2631:1: W293 blank line contains whitespace
backend/database.py:2635:1: W293 blank line contains whitespace
backend/database.py:2638:1: W293 blank line contains whitespace
backend/database.py:2643:9: E722 do not use bare 'except'
backend/database.py:2645:1: W293 blank line contains whitespace
backend/database.py:2648:1: W293 blank line contains whitespace
backend/database.py:2653:79: W291 trailing whitespace
backend/database.py:2657:1: W293 blank line contains whitespace
backend/database.py:2667:1: W293 blank line contains whitespace
backend/database.py:2673:1: W293 blank line contains whitespace
backend/database.py:2676:1: W293 blank line contains whitespace
backend/database.py:2680:1: W293 blank line contains whitespace
backend/database.py:2702:1: W293 blank line contains whitespace
backend/database.py:2704:1: W293 blank line contains whitespace
backend/database.py:2707:1: W293 blank line contains whitespace
backend/database.py:2719:1: W293 blank line contains whitespace
backend/database.py:2722:1: W293 blank line contains whitespace
backend/database.py:2728:1: W293 blank line contains whitespace
backend/database.py:2731:1: W293 blank line contains whitespace
backend/database.py:2735:1: W293 blank line contains whitespace
backend/database.py:2747:1: W293 blank line contains whitespace
backend/database.py:2750:1: W293 blank line contains whitespace
backend/database.py:2756:1: W293 blank line contains whitespace
backend/database.py:2760:28: W291 trailing whitespace
backend/database.py:2764:1: W293 blank line contains whitespace
backend/database.py:2773:67: W291 trailing whitespace
backend/database.py:2777:1: W293 blank line contains whitespace
backend/database.py:2787:1: W293 blank line contains whitespace
backend/database.py:2794:1: W293 blank line contains whitespace
backend/database.py:2798:1: W293 blank line contains whitespace
backend/database.py:2802:1: W293 blank line contains whitespace
backend/database.py:2805:62: W291 trailing whitespace
backend/database.py:2811:1: W293 blank line contains whitespace
backend/database.py:2823:1: W293 blank line contains whitespace
backend/database.py:2828:1: W293 blank line contains whitespace
backend/database.py:2834:1: W293 blank line contains whitespace
backend/database.py:2837:45: W291 trailing whitespace
backend/database.py:2839:39: W291 trailing whitespace
backend/database.py:2844:45: W291 trailing whitespace
backend/database.py:2845:39: W291 trailing whitespace
backend/database.py:2848:1: W293 blank line contains whitespace
backend/database.py:2851:1: W293 blank line contains whitespace
backend/database.py:2855:1: W293 blank line contains whitespace
backend/database.py:2865:1: W293 blank line contains whitespace
backend/database.py:2869:12: F821 undefined name 'get_db'
backend/database.py:2871:1: W293 blank line contains whitespace
backend/database.py:2873:47: W291 trailing whitespace
backend/database.py:2876:1: W293 blank line contains whitespace
backend/database.py:2885:1: W293 blank line contains whitespace
backend/database.py:2889:12: F821 undefined name 'get_db'
backend/database.py:2891:1: W293 blank line contains whitespace
backend/database.py:2893:15: W291 trailing whitespace
backend/database.py:2898:1: W293 blank line contains whitespace
backend/database.py:2901:1: W293 blank line contains whitespace
backend/database.py:2911:1: W293 blank line contains whitespace
backend/database.py:2915:12: F821 undefined name 'get_db'
backend/database.py:2917:1: W293 blank line contains whitespace
backend/database.py:2919:15: W291 trailing whitespace
backend/database.py:2924:1: W293 blank line contains whitespace
backend/database.py:2927:1: W293 blank line contains whitespace
backend/database.py:2937:1: W293 blank line contains whitespace
backend/database.py:2940:1: W293 blank line contains whitespace
backend/database.py:2946:1: W293 blank line contains whitespace
backend/database.py:2950:1: W293 blank line contains whitespace
backend/database.py:2953:39: W291 trailing whitespace
backend/database.py:2956:1: W293 blank line contains whitespace
backend/database.py:2960:1: W293 blank line contains whitespace
backend/database.py:2962:28: W291 trailing whitespace
backend/database.py:2963:86: W291 trailing whitespace
backend/database.py:2974:1: W293 blank line contains whitespace
backend/database.py:2978:1: W293 blank line contains whitespace
backend/database.py:2990:1: W293 blank line contains whitespace
backend/database.py:2992:1: W293 blank line contains whitespace
backend/database.py:2996:1: W293 blank line contains whitespace
backend/email_alerts.py:19:1: F401 'database as db' imported but unused
backend/email_alerts.py:19:1: E402 module level import not at top of file
backend/email_alerts.py:24:1: E302 expected 2 blank lines, found 1
backend/email_alerts.py:28:1: W293 blank line contains whitespace
backend/email_alerts.py:32:5: E722 do not use bare 'except'
backend/email_alerts.py:35:1: E302 expected 2 blank lines, found 1
backend/email_alerts.py:35:70: W291 trailing whitespace
backend/email_alerts.py:36:24: E127 continuation line over-indented for visual indent
backend/email_alerts.py:49:1: W293 blank line contains whitespace
backend/email_alerts.py:51:1: W293 blank line contains whitespace
backend/email_alerts.py:54:1: W293 blank line contains whitespace
backend/email_alerts.py:57:1: E302 expected 2 blank lines, found 1
backend/email_alerts.py:61:1: W293 blank line contains whitespace
backend/email_alerts.py:64:1: W293 blank line contains whitespace
backend/email_alerts.py:71:1: W293 blank line contains whitespace
backend/email_alerts.py:86:1: W293 blank line contains whitespace
backend/email_alerts.py:88:1: W293 blank line contains whitespace
backend/email_alerts.py:95:1: W293 blank line contains whitespace
backend/email_alerts.py:99:1: W293 blank line contains whitespace
backend/email_alerts.py:101:1: W293 blank line contains whitespace
backend/email_alerts.py:105:1: E302 expected 2 blank lines, found 1
backend/email_alerts.py:108:1: W293 blank line contains whitespace
backend/email_alerts.py:111:1: W293 blank line contains whitespace
backend/email_alerts.py:120:1: W293 blank line contains whitespace
backend/email_alerts.py:126:1: W293 blank line contains whitespace
backend/email_alerts.py:161:1: W293 blank line contains whitespace
backend/email_alerts.py:167:1: W293 blank line contains whitespace
backend/email_alerts.py:173:1: W293 blank line contains whitespace
backend/email_alerts.py:175:1: W293 blank line contains whitespace
backend/email_alerts.py:183:1: W293 blank line contains whitespace
backend/email_alerts.py:185:1: W293 blank line contains whitespace
backend/email_alerts.py:192:1: W293 blank line contains whitespace
backend/email_alerts.py:196:1: W293 blank line contains whitespace
backend/email_alerts.py:198:1: W293 blank line contains whitespace
backend/email_alerts.py:202:1: E302 expected 2 blank lines, found 1
backend/email_alerts.py:208:1: W293 blank line contains whitespace
backend/email_alerts.py:215:1: W293 blank line contains whitespace
backend/email_alerts.py:223:1: W293 blank line contains whitespace
backend/email_alerts.py:231:1: W293 blank line contains whitespace
backend/email_alerts.py:239:1: W293 blank line contains whitespace
backend/email_alerts.py:242:1: E305 expected 2 blank lines after class or function definition, found 1
backend/email_alerts.py:245:1: W293 blank line contains whitespace
backend/email_alerts.py:248:1: W293 blank line contains whitespace
backend/email_alerts.py:251:15: F541 f-string is missing placeholders
backend/event_model.py:10:1: F401 'typing.List' imported but unused
backend/event_model.py:19:1: W293 blank line contains whitespace
backend/event_model.py:41:1: W293 blank line contains whitespace
backend/event_model.py:45:1: W293 blank line contains whitespace
backend/event_model.py:49:1: W293 blank line contains whitespace
backend/event_model.py:68:1: W293 blank line contains whitespace
backend/event_model.py:83:1: W293 blank line contains whitespace
backend/event_model.py:90:1: W293 blank line contains whitespace
backend/event_model.py:95:1: W293 blank line contains whitespace
backend/event_model.py:99:1: W293 blank line contains whitespace
backend/event_model.py:104:1: W293 blank line contains whitespace
backend/event_model.py:111:1: W293 blank line contains whitespace
backend/event_model.py:114:1: W293 blank line contains whitespace
backend/event_model.py:118:1: W293 blank line contains whitespace
backend/event_model.py:122:1: W293 blank line contains whitespace
backend/event_model.py:157:1: W293 blank line contains whitespace
backend/inventory_collector.py:23:1: F401 'json' imported but unused
backend/inventory_collector.py:25:1: F401 'time' imported but unused
backend/inventory_collector.py:38:1: W293 blank line contains whitespace
backend/inventory_collector.py:39:60: W291 trailing whitespace
backend/inventory_collector.py:41:53: W291 trailing whitespace
backend/inventory_collector.py:46:1: W293 blank line contains whitespace
backend/inventory_collector.py:64:1: W293 blank line contains whitespace
backend/inventory_collector.py:68:1: W293 blank line contains whitespace
backend/inventory_collector.py:75:1: W293 blank line contains whitespace
backend/inventory_collector.py:84:1: W293 blank line contains whitespace
backend/inventory_collector.py:89:1: W293 blank line contains whitespace
backend/inventory_collector.py:98:1: W293 blank line contains whitespace
backend/inventory_collector.py:103:1: W293 blank line contains whitespace
backend/inventory_collector.py:112:1: W293 blank line contains whitespace
backend/inventory_collector.py:116:1: W293 blank line contains whitespace
backend/inventory_collector.py:119:1: W293 blank line contains whitespace
backend/inventory_collector.py:122:1: W293 blank line contains whitespace
backend/inventory_collector.py:128:1: W293 blank line contains whitespace
backend/inventory_collector.py:137:1: W293 blank line contains whitespace
backend/inventory_collector.py:141:1: W293 blank line contains whitespace
backend/inventory_collector.py:144:1: W293 blank line contains whitespace
backend/inventory_collector.py:150:1: W293 blank line contains whitespace
backend/inventory_collector.py:153:25: W291 trailing whitespace
backend/inventory_collector.py:158:9: F841 local variable 'e' is assigned to but never used
backend/inventory_collector.py:161:1: W293 blank line contains whitespace
backend/inventory_collector.py:165:1: W293 blank line contains whitespace
backend/inventory_collector.py:179:1: W293 blank line contains whitespace
backend/inventory_collector.py:185:1: W293 blank line contains whitespace
backend/inventory_collector.py:190:1: W293 blank line contains whitespace
backend/inventory_collector.py:192:1: W293 blank line contains whitespace
backend/inventory_collector.py:197:1: W293 blank line contains whitespace
backend/inventory_collector.py:201:1: W293 blank line contains whitespace
backend/inventory_collector.py:208:1: W293 blank line contains whitespace
backend/inventory_collector.py:214:13: E722 do not use bare 'except'
backend/inventory_collector.py:216:1: W293 blank line contains whitespace
backend/inventory_collector.py:222:1: W293 blank line contains whitespace
backend/inventory_collector.py:224:1: W293 blank line contains whitespace
backend/inventory_collector.py:228:1: W293 blank line contains whitespace
backend/inventory_collector.py:241:1: W293 blank line contains whitespace
backend/inventory_collector.py:245:1: W293 blank line contains whitespace
backend/inventory_collector.py:252:17: E722 do not use bare 'except'
backend/inventory_collector.py:254:1: W293 blank line contains whitespace
backend/inventory_collector.py:256:1: W293 blank line contains whitespace
backend/inventory_collector.py:260:1: W293 blank line contains whitespace
backend/inventory_collector.py:271:1: W293 blank line contains whitespace
backend/inventory_collector.py:277:1: W293 blank line contains whitespace
backend/inventory_collector.py:279:1: W293 blank line contains whitespace
backend/inventory_collector.py:283:1: W293 blank line contains whitespace
backend/inventory_collector.py:297:1: W293 blank line contains whitespace
backend/inventory_collector.py:299:1: W293 blank line contains whitespace
backend/inventory_collector.py:303:1: W293 blank line contains whitespace
backend/inventory_collector.py:311:1: W293 blank line contains whitespace
backend/inventory_collector.py:319:1: W293 blank line contains whitespace
backend/inventory_collector.py:324:1: W293 blank line contains whitespace
backend/inventory_collector.py:326:1: W293 blank line contains whitespace
backend/inventory_collector.py:330:1: W293 blank line contains whitespace
backend/inventory_collector.py:336:1: W293 blank line contains whitespace
backend/inventory_collector.py:341:1: W293 blank line contains whitespace
backend/inventory_collector.py:346:1: W293 blank line contains whitespace
backend/inventory_collector.py:348:1: W293 blank line contains whitespace
backend/inventory_collector.py:352:1: W293 blank line contains whitespace
backend/inventory_collector.py:359:1: W293 blank line contains whitespace
backend/inventory_collector.py:361:1: W293 blank line contains whitespace
backend/inventory_collector.py:362:58: W291 trailing whitespace
backend/inventory_collector.py:363:20: E128 continuation line under-indented for visual indent
backend/inventory_collector.py:366:1: W293 blank line contains whitespace
backend/inventory_collector.py:370:1: W293 blank line contains whitespace
backend/inventory_collector.py:385:1: W293 blank line contains whitespace
backend/inventory_collector.py:395:1: W293 blank line contains whitespace
backend/inventory_collector.py:398:1: W293 blank line contains whitespace
backend/inventory_collector.py:401:1: W293 blank line contains whitespace
backend/inventory_collector.py:404:1: W293 blank line contains whitespace
backend/inventory_collector.py:407:1: W293 blank line contains whitespace
backend/inventory_collector.py:410:1: W293 blank line contains whitespace
backend/inventory_collector.py:413:1: W293 blank line contains whitespace
backend/inventory_collector.py:417:1: W293 blank line contains whitespace
backend/inventory_collector.py:421:1: W293 blank line contains whitespace
backend/inventory_collector.py:425:1: W293 blank line contains whitespace
backend/inventory_collector.py:430:29: E128 continuation line under-indented for visual indent
backend/inventory_collector.py:431:29: E128 continuation line under-indented for visual indent
backend/inventory_collector.py:432:29: E128 continuation line under-indented for visual indent
backend/inventory_collector.py:435:1: W293 blank line contains whitespace
backend/inventory_collector.py:442:1: W293 blank line contains whitespace
backend/inventory_collector.py:457:1: W293 blank line contains whitespace
backend/inventory_collector.py:460:1: W293 blank line contains whitespace
backend/inventory_collector.py:466:1: W293 blank line contains whitespace
backend/inventory_collector.py:468:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:64:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v2.py:69:5: E722 do not use bare 'except'
backend/legacy/server_dashboard_api_v2.py:72:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v2.py:81:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:89:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:94:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:99:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:102:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:107:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:130:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v2.py:133:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:138:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:145:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:148:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:155:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:162:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:168:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:172:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:181:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v2.py:184:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:189:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:193:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:199:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:202:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:209:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:215:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:221:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:228:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v2.py:232:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:250:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:253:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v2.py:257:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:260:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:265:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:269:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:273:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:278:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:286:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:290:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v2.py:294:38: W291 trailing whitespace
backend/legacy/server_dashboard_api_v2.py:303:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:308:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:316:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:319:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v2.py:325:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:328:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:341:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:344:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v2.py:352:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:355:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:359:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:363:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v2.py:368:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:381:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:384:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:391:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v2.py:395:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:399:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:402:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v2.py:406:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:412:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:418:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v2.py:421:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:424:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:439:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v2.py:440:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:448:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:451:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:455:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:460:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:465:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:470:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:475:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:480:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:485:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:490:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:497:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:502:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:507:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:512:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:517:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:527:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:543:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:547:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:551:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:554:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:559:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:563:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:565:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:571:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:575:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:578:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:582:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:584:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:590:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:594:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:597:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:601:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:603:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:609:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:614:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:620:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:624:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:628:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v2.py:632:1: E305 expected 2 blank lines after class or function definition, found 1
backend/legacy/server_dashboard_api_v3.py:64:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v3.py:69:5: E722 do not use bare 'except'
backend/legacy/server_dashboard_api_v3.py:72:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v3.py:81:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:89:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:94:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:99:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:102:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:107:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:130:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v3.py:133:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:138:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:145:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:148:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:155:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:162:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:168:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:172:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:181:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v3.py:184:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:189:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:193:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:199:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:202:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:209:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:215:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:221:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:228:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v3.py:232:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:250:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:253:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v3.py:257:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:260:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:265:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:269:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:273:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:278:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:286:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:290:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v3.py:294:38: W291 trailing whitespace
backend/legacy/server_dashboard_api_v3.py:303:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:308:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:316:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:319:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v3.py:325:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:328:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:341:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:344:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v3.py:352:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:355:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:359:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:363:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v3.py:368:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:381:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:384:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:391:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v3.py:395:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:399:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:402:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v3.py:406:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:412:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:418:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v3.py:421:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:424:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:439:1: E302 expected 2 blank lines, found 1
backend/legacy/server_dashboard_api_v3.py:440:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:448:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:451:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:455:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:460:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:465:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:470:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:475:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:480:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:485:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:490:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:497:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:502:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:507:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:512:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:517:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:527:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:543:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:547:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:551:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:554:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:559:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:563:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:565:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:571:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:575:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:578:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:582:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:584:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:590:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:594:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:597:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:601:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:603:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:609:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:614:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:620:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:624:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:628:1: W293 blank line contains whitespace
backend/legacy/server_dashboard_api_v3.py:632:1: E305 expected 2 blank lines after class or function definition, found 1
backend/legacy/status_webserver.py:10:1: E302 expected 2 blank lines, found 1
backend/legacy/status_webserver.py:13:1: W293 blank line contains whitespace
backend/legacy/status_webserver.py:18:1: E305 expected 2 blank lines after class or function definition, found 1
backend/migrations/migrate.py:10:1: F401 'datetime.datetime' imported but unused
backend/migrations/migrate.py:19:1: E302 expected 2 blank lines, found 1
backend/migrations/migrate.py:23:1: E302 expected 2 blank lines, found 1
backend/migrations/migrate.py:27:1: W293 blank line contains whitespace
backend/migrations/migrate.py:36:1: W293 blank line contains whitespace
backend/migrations/migrate.py:40:1: E302 expected 2 blank lines, found 1
backend/migrations/migrate.py:44:1: W293 blank line contains whitespace
backend/migrations/migrate.py:47:1: W293 blank line contains whitespace
backend/migrations/migrate.py:51:1: E302 expected 2 blank lines, found 1
backend/migrations/migrate.py:55:1: W293 blank line contains whitespace
backend/migrations/migrate.py:60:1: W293 blank line contains whitespace
backend/migrations/migrate.py:67:1: E302 expected 2 blank lines, found 1
backend/migrations/migrate.py:71:1: W293 blank line contains whitespace
backend/migrations/migrate.py:75:1: W293 blank line contains whitespace
backend/migrations/migrate.py:77:1: W293 blank line contains whitespace
backend/migrations/migrate.py:80:1: W293 blank line contains whitespace
backend/migrations/migrate.py:85:1: W293 blank line contains whitespace
backend/migrations/migrate.py:88:40: W291 trailing whitespace
backend/migrations/migrate.py:92:1: W293 blank line contains whitespace
backend/migrations/migrate.py:95:40: W291 trailing whitespace
backend/migrations/migrate.py:99:1: W293 blank line contains whitespace
backend/migrations/migrate.py:103:1: W293 blank line contains whitespace
backend/migrations/migrate.py:114:1: E302 expected 2 blank lines, found 1
backend/migrations/migrate.py:118:1: W293 blank line contains whitespace
backend/migrations/migrate.py:122:1: W293 blank line contains whitespace
backend/migrations/migrate.py:124:1: W293 blank line contains whitespace
backend/migrations/migrate.py:127:1: W293 blank line contains whitespace
backend/migrations/migrate.py:143:1: W293 blank line contains whitespace
backend/migrations/migrate.py:157:1: W293 blank line contains whitespace
backend/migrations/migrate.py:161:1: W293 blank line contains whitespace
backend/migrations/migrate.py:172:1: E302 expected 2 blank lines, found 1
backend/migrations/migrate.py:176:1: W293 blank line contains whitespace
backend/migrations/migrate.py:180:1: W293 blank line contains whitespace
backend/migrations/migrate.py:182:1: W293 blank line contains whitespace
backend/migrations/migrate.py:185:1: W293 blank line contains whitespace
backend/migrations/migrate.py:202:1: W293 blank line contains whitespace
backend/migrations/migrate.py:206:1: W293 blank line contains whitespace
backend/migrations/migrate.py:217:1: E302 expected 2 blank lines, found 1
backend/migrations/migrate.py:221:1: W293 blank line contains whitespace
backend/migrations/migrate.py:225:1: W293 blank line contains whitespace
backend/migrations/migrate.py:227:1: W293 blank line contains whitespace
backend/migrations/migrate.py:230:1: W293 blank line contains whitespace
backend/migrations/migrate.py:247:1: W293 blank line contains whitespace
backend/migrations/migrate.py:251:1: W293 blank line contains whitespace
backend/migrations/migrate.py:262:1: E302 expected 2 blank lines, found 1
backend/migrations/migrate.py:266:1: W293 blank line contains whitespace
backend/migrations/migrate.py:270:1: W293 blank line contains whitespace
backend/migrations/migrate.py:272:1: W293 blank line contains whitespace
backend/migrations/migrate.py:275:1: W293 blank line contains whitespace
backend/migrations/migrate.py:292:1: W293 blank line contains whitespace
backend/migrations/migrate.py:296:1: W293 blank line contains whitespace
backend/migrations/migrate.py:307:1: E302 expected 2 blank lines, found 1
backend/migrations/migrate.py:311:1: W293 blank line contains whitespace
backend/migrations/migrate.py:315:1: W293 blank line contains whitespace
backend/migrations/migrate.py:317:1: W293 blank line contains whitespace
backend/migrations/migrate.py:320:1: W293 blank line contains whitespace
backend/migrations/migrate.py:340:1: W293 blank line contains whitespace
backend/migrations/migrate.py:347:1: W293 blank line contains whitespace
backend/migrations/migrate.py:351:1: W293 blank line contains whitespace
backend/migrations/migrate.py:362:1: E302 expected 2 blank lines, found 1
backend/migrations/migrate.py:368:1: W293 blank line contains whitespace
backend/migrations/migrate.py:371:1: W293 blank line contains whitespace
backend/migrations/migrate.py:383:1: W293 blank line contains whitespace
backend/migrations/migrate.py:391:1: W293 blank line contains whitespace
backend/migrations/migrate.py:398:1: E305 expected 2 blank lines after class or function definition, found 1
backend/migrations/migrate.py:404:1: E302 expected 2 blank lines, found 1
backend/migrations/migrate.py:408:1: W293 blank line contains whitespace
backend/migrations/migrate.py:412:1: W293 blank line contains whitespace
backend/migrations/migrate.py:414:1: W293 blank line contains whitespace
backend/migrations/migrate.py:417:1: W293 blank line contains whitespace
backend/migrations/migrate.py:440:1: W293 blank line contains whitespace
backend/migrations/migrate.py:443:59: W291 trailing whitespace
backend/migrations/migrate.py:446:1: W293 blank line contains whitespace
backend/migrations/migrate.py:448:57: W291 trailing whitespace
backend/migrations/migrate.py:451:1: W293 blank line contains whitespace
backend/migrations/migrate.py:453:56: W291 trailing whitespace
backend/migrations/migrate.py:456:1: W293 blank line contains whitespace
backend/migrations/migrate.py:458:60: W291 trailing whitespace
backend/migrations/migrate.py:462:1: W293 blank line contains whitespace
backend/migrations/migrate.py:466:1: W293 blank line contains whitespace
backend/migrations/migrate.py:477:1: E302 expected 2 blank lines, found 1
backend/migrations/migrate.py:481:1: W293 blank line contains whitespace
backend/migrations/migrate.py:485:1: W293 blank line contains whitespace
backend/migrations/migrate.py:487:1: W293 blank line contains whitespace
backend/migrations/migrate.py:490:1: W293 blank line contains whitespace
backend/migrations/migrate.py:495:1: W293 blank line contains whitespace
backend/migrations/migrate.py:499:41: W291 trailing whitespace
backend/migrations/migrate.py:503:1: W293 blank line contains whitespace
backend/migrations/migrate.py:506:41: W291 trailing whitespace
backend/migrations/migrate.py:510:1: W293 blank line contains whitespace
backend/migrations/migrate.py:524:1: W293 blank line contains whitespace
backend/migrations/migrate.py:540:1: W293 blank line contains whitespace
backend/migrations/migrate.py:543:68: W291 trailing whitespace
backend/migrations/migrate.py:546:1: W293 blank line contains whitespace
backend/migrations/migrate.py:548:65: W291 trailing whitespace
backend/migrations/migrate.py:552:1: W293 blank line contains whitespace
backend/migrations/migrate.py:556:1: W293 blank line contains whitespace
backend/observability.py:43:1: W293 blank line contains whitespace
backend/observability.py:46:1: W293 blank line contains whitespace
backend/observability.py:55:1: W293 blank line contains whitespace
backend/observability.py:64:1: W293 blank line contains whitespace
backend/observability.py:66:1: W293 blank line contains whitespace
backend/observability.py:70:1: W293 blank line contains whitespace
backend/observability.py:74:1: W293 blank line contains whitespace
backend/observability.py:78:1: W293 blank line contains whitespace
backend/observability.py:82:1: W293 blank line contains whitespace
backend/observability.py:83:83: W291 trailing whitespace
backend/observability.py:106:1: W293 blank line contains whitespace
backend/observability.py:111:1: W293 blank line contains whitespace
backend/observability.py:114:1: W293 blank line contains whitespace
backend/observability.py:123:1: W293 blank line contains whitespace
backend/observability.py:126:1: W293 blank line contains whitespace
backend/observability.py:128:1: W293 blank line contains whitespace
backend/observability.py:133:1: W293 blank line contains whitespace
backend/observability.py:136:1: W293 blank line contains whitespace
backend/observability.py:150:1: W293 blank line contains whitespace
backend/observability.py:159:1: W293 blank line contains whitespace
backend/observability.py:164:1: W293 blank line contains whitespace
backend/observability.py:168:1: W293 blank line contains whitespace
backend/observability.py:186:1: W293 blank line contains whitespace
backend/observability.py:196:1: W293 blank line contains whitespace
backend/observability.py:198:1: W293 blank line contains whitespace
backend/observability.py:202:1: W293 blank line contains whitespace
backend/observability.py:207:1: W293 blank line contains whitespace
backend/observability.py:213:1: W293 blank line contains whitespace
backend/observability.py:221:1: W293 blank line contains whitespace
backend/observability.py:233:1: W293 blank line contains whitespace
backend/observability.py:238:1: W293 blank line contains whitespace
backend/observability.py:243:1: W293 blank line contains whitespace
backend/observability.py:248:1: W293 blank line contains whitespace
backend/observability.py:252:1: W293 blank line contains whitespace
backend/observability.py:260:1: W293 blank line contains whitespace
backend/observability.py:265:1: W293 blank line contains whitespace
backend/observability.py:273:1: W293 blank line contains whitespace
backend/observability.py:283:1: W293 blank line contains whitespace
backend/observability.py:289:1: W293 blank line contains whitespace
backend/observability.py:302:1: W293 blank line contains whitespace
backend/observability.py:316:1: W293 blank line contains whitespace
backend/observability.py:331:1: W293 blank line contains whitespace
backend/observability.py:333:1: W293 blank line contains whitespace
backend/observability.py:340:1: W293 blank line contains whitespace
backend/observability.py:354:1: W293 blank line contains whitespace
backend/observability.py:367:1: W293 blank line contains whitespace
backend/observability.py:379:1: W293 blank line contains whitespace
backend/observability.py:390:1: E302 expected 2 blank lines, found 1
backend/plugin_system.py:11:1: F401 'typing.Callable' imported but unused
backend/plugin_system.py:14:1: F401 'abc.abstractmethod' imported but unused
backend/plugin_system.py:19:1: E402 module level import not at top of file
backend/plugin_system.py:20:1: E402 module level import not at top of file
backend/plugin_system.py:29:1: W293 blank line contains whitespace
backend/plugin_system.py:33:1: W293 blank line contains whitespace
backend/plugin_system.py:37:1: W293 blank line contains whitespace
backend/plugin_system.py:44:1: W293 blank line contains whitespace
backend/plugin_system.py:48:1: W293 blank line contains whitespace
backend/plugin_system.py:53:1: W293 blank line contains whitespace
backend/plugin_system.py:57:1: W293 blank line contains whitespace
backend/plugin_system.py:61:1: W293 blank line contains whitespace
backend/plugin_system.py:66:1: W293 blank line contains whitespace
backend/plugin_system.py:70:1: W293 blank line contains whitespace
backend/plugin_system.py:75:1: W293 blank line contains whitespace
backend/plugin_system.py:79:1: W293 blank line contains whitespace
backend/plugin_system.py:84:1: W293 blank line contains whitespace
backend/plugin_system.py:88:1: W293 blank line contains whitespace
backend/plugin_system.py:93:1: W293 blank line contains whitespace
backend/plugin_system.py:97:1: W293 blank line contains whitespace
backend/plugin_system.py:102:1: W293 blank line contains whitespace
backend/plugin_system.py:106:1: W293 blank line contains whitespace
backend/plugin_system.py:111:1: W293 blank line contains whitespace
backend/plugin_system.py:115:1: W293 blank line contains whitespace
backend/plugin_system.py:125:1: W293 blank line contains whitespace
backend/plugin_system.py:132:1: W293 blank line contains whitespace
backend/plugin_system.py:138:1: W293 blank line contains whitespace
backend/plugin_system.py:140:20: E128 continuation line under-indented for visual indent
backend/plugin_system.py:141:20: E128 continuation line under-indented for visual indent
backend/plugin_system.py:142:20: E128 continuation line under-indented for visual indent
backend/plugin_system.py:143:1: W293 blank line contains whitespace
backend/plugin_system.py:150:1: W293 blank line contains whitespace
backend/plugin_system.py:154:1: W293 blank line contains whitespace
backend/plugin_system.py:161:1: W293 blank line contains whitespace
backend/plugin_system.py:165:1: W293 blank line contains whitespace
backend/plugin_system.py:168:26: E128 continuation line under-indented for visual indent
backend/plugin_system.py:170:1: W293 blank line contains whitespace
backend/plugin_system.py:176:28: E128 continuation line under-indented for visual indent
backend/plugin_system.py:177:28: E128 continuation line under-indented for visual indent
backend/plugin_system.py:178:1: W293 blank line contains whitespace
backend/plugin_system.py:182:1: W293 blank line contains whitespace
backend/plugin_system.py:187:1: W293 blank line contains whitespace
backend/plugin_system.py:190:25: E128 continuation line under-indented for visual indent
backend/plugin_system.py:192:1: W293 blank line contains whitespace
backend/plugin_system.py:201:1: W293 blank line contains whitespace
backend/plugin_system.py:205:1: W293 blank line contains whitespace
backend/plugin_system.py:210:43: W291 trailing whitespace
backend/plugin_system.py:211:54: W291 trailing whitespace
backend/plugin_system.py:212:17: E129 visually indented line with same indent as next logical line
backend/plugin_system.py:215:1: W293 blank line contains whitespace
backend/plugin_system.py:219:1: W293 blank line contains whitespace
backend/plugin_system.py:228:13: E722 do not use bare 'except'
backend/plugin_system.py:230:30: E128 continuation line under-indented for visual indent
backend/plugin_system.py:231:1: W293 blank line contains whitespace
backend/plugin_system.py:235:1: W293 blank line contains whitespace
backend/plugin_system.py:237:20: E128 continuation line under-indented for visual indent
backend/plugin_system.py:238:20: E128 continuation line under-indented for visual indent
backend/plugin_system.py:239:1: W293 blank line contains whitespace
backend/plugin_system.py:243:1: W293 blank line contains whitespace
backend/plugin_system.py:246:1: W293 blank line contains whitespace
backend/plugin_system.py:251:1: W293 blank line contains whitespace
backend/plugin_system.py:255:1: W293 blank line contains whitespace
backend/plugin_system.py:259:1: W293 blank line contains whitespace
backend/plugin_system.py:262:1: W293 blank line contains whitespace
backend/plugin_system.py:265:28: E128 continuation line under-indented for visual indent
backend/plugin_system.py:266:28: E128 continuation line under-indented for visual indent
backend/plugin_system.py:267:28: E128 continuation line under-indented for visual indent
backend/plugin_system.py:268:28: E128 continuation line under-indented for visual indent
backend/plugin_system.py:269:1: W293 blank line contains whitespace
backend/plugin_system.py:273:1: W293 blank line contains whitespace
backend/plugin_system.py:279:1: W293 blank line contains whitespace
backend/plugin_system.py:291:1: W293 blank line contains whitespace
backend/plugin_system.py:295:1: W293 blank line contains whitespace
backend/plugin_system.py:299:1: W293 blank line contains whitespace
backend/plugin_system.py:305:1: W293 blank line contains whitespace
backend/plugin_system.py:310:1: W293 blank line contains whitespace
backend/plugin_system.py:314:28: E128 continuation line under-indented for visual indent
backend/plugin_system.py:317:28: E128 continuation line under-indented for visual indent
backend/plugin_system.py:318:28: E128 continuation line under-indented for visual indent
backend/plugin_system.py:319:1: W293 blank line contains whitespace
backend/plugin_system.py:324:1: W293 blank line contains whitespace
backend/plugin_system.py:329:28: E128 continuation line under-indented for visual indent
backend/plugin_system.py:332:28: E128 continuation line under-indented for visual indent
backend/plugin_system.py:333:28: E128 continuation line under-indented for visual indent
backend/plugin_system.py:352:1: W293 blank line contains whitespace
backend/plugin_system.py:354:1: W293 blank line contains whitespace
backend/plugins/webhook.py:10:1: F401 'json' imported but unused
backend/plugins/webhook.py:20:1: E402 module level import not at top of file
backend/plugins/webhook.py:21:1: F401 'event_model.EventTypes' imported but unused
backend/plugins/webhook.py:21:1: E402 module level import not at top of file
backend/plugins/webhook.py:22:1: E402 module level import not at top of file
backend/plugins/webhook.py:31:1: W293 blank line contains whitespace
backend/plugins/webhook.py:40:1: W293 blank line contains whitespace
backend/plugins/webhook.py:46:1: W293 blank line contains whitespace
backend/plugins/webhook.py:49:1: W293 blank line contains whitespace
backend/plugins/webhook.py:55:1: W293 blank line contains whitespace
backend/plugins/webhook.py:60:1: W293 blank line contains whitespace
backend/plugins/webhook.py:63:24: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:64:24: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:65:24: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:66:1: W293 blank line contains whitespace
backend/plugins/webhook.py:71:1: W293 blank line contains whitespace
backend/plugins/webhook.py:75:1: W293 blank line contains whitespace
backend/plugins/webhook.py:81:1: W293 blank line contains whitespace
backend/plugins/webhook.py:85:1: W293 blank line contains whitespace
backend/plugins/webhook.py:87:1: W293 blank line contains whitespace
backend/plugins/webhook.py:91:1: W293 blank line contains whitespace
backend/plugins/webhook.py:98:1: W293 blank line contains whitespace
backend/plugins/webhook.py:107:1: W293 blank line contains whitespace
backend/plugins/webhook.py:115:1: W293 blank line contains whitespace
backend/plugins/webhook.py:118:1: W293 blank line contains whitespace
backend/plugins/webhook.py:125:1: W293 blank line contains whitespace
backend/plugins/webhook.py:133:36: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:134:36: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:135:36: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:136:36: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:137:36: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:142:34: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:143:34: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:144:34: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:145:34: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:146:34: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:147:34: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:153:34: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:154:34: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:155:34: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:156:34: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:157:34: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:158:34: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:159:1: W293 blank line contains whitespace
backend/plugins/webhook.py:164:1: W293 blank line contains whitespace
backend/plugins/webhook.py:167:25: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:168:25: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:169:25: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:170:25: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:171:25: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:172:1: W293 blank line contains whitespace
backend/plugins/webhook.py:175:25: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:176:25: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:177:25: E128 continuation line under-indented for visual indent
backend/plugins/webhook.py:178:1: W293 blank line contains whitespace
backend/rate_limiter.py:27:1: W293 blank line contains whitespace
backend/rate_limiter.py:34:1: W293 blank line contains whitespace
backend/rate_limiter.py:38:1: W293 blank line contains whitespace
backend/rate_limiter.py:47:1: W293 blank line contains whitespace
backend/rate_limiter.py:52:1: W293 blank line contains whitespace
backend/rate_limiter.py:59:1: W293 blank line contains whitespace
backend/rate_limiter.py:66:1: W293 blank line contains whitespace
backend/rate_limiter.py:68:1: W293 blank line contains whitespace
backend/rate_limiter.py:72:1: W293 blank line contains whitespace
backend/rate_limiter.py:76:1: W293 blank line contains whitespace
backend/rate_limiter.py:83:1: W293 blank line contains whitespace
backend/rate_limiter.py:91:1: W293 blank line contains whitespace
backend/rate_limiter.py:99:1: W293 blank line contains whitespace
backend/rate_limiter.py:102:30: E128 continuation line under-indented for visual indent
backend/rate_limiter.py:103:30: E128 continuation line under-indented for visual indent
backend/rate_limiter.py:104:30: E128 continuation line under-indented for visual indent
backend/rate_limiter.py:105:30: E128 continuation line under-indented for visual indent
backend/rate_limiter.py:106:1: W293 blank line contains whitespace
backend/rate_limiter.py:108:1: W293 blank line contains whitespace
backend/rate_limiter.py:112:1: W293 blank line contains whitespace
backend/rate_limiter.py:119:1: W293 blank line contains whitespace
backend/rate_limiter.py:124:1: W293 blank line contains whitespace
backend/rate_limiter.py:128:1: W293 blank line contains whitespace
backend/rate_limiter.py:135:1: W293 blank line contains whitespace
backend/rate_limiter.py:139:1: W293 blank line contains whitespace
backend/rate_limiter.py:142:1: W293 blank line contains whitespace
backend/rate_limiter.py:155:1: W293 blank line contains whitespace
backend/rate_limiter.py:160:1: W293 blank line contains whitespace
backend/rate_limiter.py:165:1: W293 blank line contains whitespace
backend/rate_limiter.py:192:1: W293 blank line contains whitespace
backend/rate_limiter.py:196:1: W293 blank line contains whitespace
backend/rate_limiter.py:203:1: W293 blank line contains whitespace
backend/rate_limiter.py:206:1: W293 blank line contains whitespace
backend/security.py:15:1: F401 'typing.Callable' imported but unused
backend/security.py:45:1: W293 blank line contains whitespace
backend/security.py:50:1: W293 blank line contains whitespace
backend/security.py:63:1: W293 blank line contains whitespace
backend/security.py:67:1: W293 blank line contains whitespace
backend/security.py:72:1: W293 blank line contains whitespace
backend/security.py:83:1: W293 blank line contains whitespace
backend/security.py:86:1: W293 blank line contains whitespace
backend/security.py:92:1: W293 blank line contains whitespace
backend/security.py:95:1: W293 blank line contains whitespace
backend/security.py:100:1: W293 blank line contains whitespace
backend/security.py:109:1: W293 blank line contains whitespace
backend/security.py:112:1: W293 blank line contains whitespace
backend/security.py:118:1: W293 blank line contains whitespace
backend/security.py:124:1: W293 blank line contains whitespace
backend/security.py:134:1: W293 blank line contains whitespace
backend/security.py:141:1: W293 blank line contains whitespace
backend/security.py:147:1: W293 blank line contains whitespace
backend/security.py:159:1: W293 blank line contains whitespace
backend/security.py:188:1: W293 blank line contains whitespace
backend/security.py:194:1: W293 blank line contains whitespace
backend/security.py:197:1: W293 blank line contains whitespace
backend/security.py:200:1: W293 blank line contains whitespace
backend/security.py:204:1: W293 blank line contains whitespace
backend/security.py:206:1: W293 blank line contains whitespace
backend/security.py:214:1: W293 blank line contains whitespace
backend/security.py:222:1: W293 blank line contains whitespace
backend/security.py:226:1: W293 blank line contains whitespace
backend/security.py:238:1: W293 blank line contains whitespace
backend/security.py:256:1: W293 blank line contains whitespace
backend/security.py:259:1: W293 blank line contains whitespace
backend/security.py:262:1: W293 blank line contains whitespace
backend/security.py:276:1: W293 blank line contains whitespace
backend/security.py:282:1: W293 blank line contains whitespace
backend/security.py:288:1: W293 blank line contains whitespace
backend/security.py:298:1: W293 blank line contains whitespace
backend/security.py:300:61: W291 trailing whitespace
backend/security.py:304:1: W293 blank line contains whitespace
backend/security.py:306:61: W291 trailing whitespace
backend/security.py:310:1: W293 blank line contains whitespace
backend/security.py:312:62: W291 trailing whitespace
backend/security.py:353:1: W293 blank line contains whitespace
backend/security.py:366:1: W293 blank line contains whitespace
backend/security.py:377:1: W293 blank line contains whitespace
backend/security.py:383:1: W293 blank line contains whitespace
backend/security.py:387:1: W293 blank line contains whitespace
backend/security.py:389:1: W293 blank line contains whitespace
backend/security.py:405:1: W293 blank line contains whitespace
backend/security.py:416:1: W293 blank line contains whitespace
backend/security.py:426:1: W293 blank line contains whitespace
backend/security.py:429:1: W293 blank line contains whitespace
backend/security.py:432:1: W293 blank line contains whitespace
backend/security.py:434:1: W293 blank line contains whitespace
backend/security.py:450:1: W293 blank line contains whitespace
backend/security.py:461:1: W293 blank line contains whitespace
backend/security.py:464:1: W293 blank line contains whitespace
backend/security.py:467:1: W293 blank line contains whitespace
backend/security.py:483:1: W293 blank line contains whitespace
backend/security.py:486:1: W293 blank line contains whitespace
backend/security.py:490:1: W293 blank line contains whitespace
backend/security.py:496:1: W293 blank line contains whitespace
backend/security.py:505:1: W293 blank line contains whitespace
backend/security.py:508:1: W293 blank line contains whitespace
backend/settings_manager.py:10:1: F401 'typing.List' imported but unused
backend/settings_manager.py:77:1: W293 blank line contains whitespace
backend/settings_manager.py:82:1: W293 blank line contains whitespace
backend/settings_manager.py:85:43: W291 trailing whitespace
backend/settings_manager.py:88:1: W293 blank line contains whitespace
backend/settings_manager.py:100:1: W293 blank line contains whitespace
backend/settings_manager.py:103:1: W293 blank line contains whitespace
backend/settings_manager.py:109:1: W293 blank line contains whitespace
backend/settings_manager.py:115:1: W293 blank line contains whitespace
backend/settings_manager.py:120:1: W293 blank line contains whitespace
backend/settings_manager.py:123:1: W293 blank line contains whitespace
backend/settings_manager.py:129:1: W293 blank line contains whitespace
backend/settings_manager.py:135:1: W293 blank line contains whitespace
backend/settings_manager.py:139:1: W293 blank line contains whitespace
backend/settings_manager.py:143:1: W293 blank line contains whitespace
backend/settings_manager.py:147:1: W293 blank line contains whitespace
backend/settings_manager.py:158:1: W293 blank line contains whitespace
backend/settings_manager.py:162:1: W293 blank line contains whitespace
backend/settings_manager.py:168:1: W293 blank line contains whitespace
backend/settings_manager.py:172:1: W293 blank line contains whitespace
backend/settings_manager.py:178:1: W293 blank line contains whitespace
backend/settings_manager.py:190:1: W293 blank line contains whitespace
backend/settings_manager.py:192:1: W293 blank line contains whitespace
backend/settings_manager.py:196:1: W293 blank line contains whitespace
backend/settings_manager.py:206:1: W293 blank line contains whitespace
backend/settings_manager.py:210:1: W293 blank line contains whitespace
backend/settings_manager.py:213:1: W293 blank line contains whitespace
backend/settings_manager.py:216:1: W293 blank line contains whitespace
backend/settings_manager.py:219:1: W293 blank line contains whitespace
backend/settings_manager.py:222:1: W293 blank line contains whitespace
backend/settings_manager.py:226:1: W293 blank line contains whitespace
backend/settings_manager.py:229:1: W293 blank line contains whitespace
backend/settings_manager.py:232:55: W291 trailing whitespace
backend/settings_manager.py:236:1: W293 blank line contains whitespace
backend/settings_manager.py:239:1: W293 blank line contains whitespace
backend/settings_manager.py:241:1: W293 blank line contains whitespace
backend/settings_manager.py:244:1: W293 blank line contains whitespace
backend/settings_manager.py:251:1: W293 blank line contains whitespace
backend/settings_manager.py:256:1: W293 blank line contains whitespace
backend/settings_manager.py:259:1: W293 blank line contains whitespace
backend/settings_manager.py:261:1: W293 blank line contains whitespace
backend/settings_manager.py:267:1: W293 blank line contains whitespace
backend/settings_manager.py:271:1: W293 blank line contains whitespace
backend/settings_manager.py:273:59: W291 trailing whitespace
backend/settings_manager.py:277:1: W293 blank line contains whitespace
backend/settings_manager.py:280:1: W293 blank line contains whitespace
backend/settings_manager.py:282:1: W293 blank line contains whitespace
backend/settings_manager.py:285:1: W293 blank line contains whitespace
backend/settings_manager.py:300:1: E302 expected 2 blank lines, found 1
backend/slack_integration.py:9:1: F401 'sys' imported but unused
backend/slack_integration.py:45:1: W293 blank line contains whitespace
backend/slack_integration.py:48:1: W293 blank line contains whitespace
backend/slack_integration.py:50:1: W293 blank line contains whitespace
backend/slack_integration.py:53:1: W293 blank line contains whitespace
backend/slack_integration.py:69:102: E502 the backslash is redundant between brackets
backend/slack_integration.py:70:95: E502 the backslash is redundant between brackets
backend/slack_integration.py:76:1: W293 blank line contains whitespace
backend/slack_integration.py:90:1: W293 blank line contains whitespace
backend/slack_integration.py:108:1: W293 blank line contains whitespace
backend/slack_integration.py:111:1: W293 blank line contains whitespace
backend/slack_integration.py:119:1: W293 blank line contains whitespace
backend/slack_integration.py:127:1: W293 blank line contains whitespace
backend/slack_integration.py:145:1: W293 blank line contains whitespace
backend/slack_integration.py:148:1: W293 blank line contains whitespace
backend/slack_integration.py:155:1: W293 blank line contains whitespace
backend/slack_integration.py:158:15: F541 f-string is missing placeholders
backend/slack_integration.py:164:1: W391 blank line at end of file
backend/ssh_key_manager.py:29:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:37:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:41:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:47:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:52:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:72:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:75:67: W291 trailing whitespace
backend/ssh_key_manager.py:78:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:80:67: W291 trailing whitespace
backend/ssh_key_manager.py:83:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:90:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:96:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:100:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:103:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:106:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:113:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:115:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:124:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:127:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:142:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:147:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:149:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:153:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:156:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:163:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:167:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:171:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:174:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:176:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:178:14: W291 trailing whitespace
backend/ssh_key_manager.py:179:19: W291 trailing whitespace
backend/ssh_key_manager.py:186:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:192:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:195:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:202:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:206:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:209:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:213:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:216:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:231:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:233:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:243:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:254:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:258:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:261:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:267:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:273:43: W291 trailing whitespace
backend/ssh_key_manager.py:274:45: W291 trailing whitespace
backend/ssh_key_manager.py:277:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:280:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:293:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:305:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:307:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:310:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:314:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:318:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:324:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:330:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:333:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:336:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:347:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:359:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:362:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:366:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:369:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:372:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:375:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:381:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:384:53: W291 trailing whitespace
backend/ssh_key_manager.py:385:30: W291 trailing whitespace
backend/ssh_key_manager.py:388:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:392:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:400:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:402:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:405:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:409:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:412:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:418:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:421:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:423:32: W291 trailing whitespace
backend/ssh_key_manager.py:427:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:429:1: W293 blank line contains whitespace
backend/ssh_key_manager.py:431:1: W293 blank line contains whitespace
backend/ssh_manager.py:10:1: F401 'socket' imported but unused
backend/ssh_manager.py:12:1: F401 'threading.Thread' imported but unused
backend/ssh_manager.py:16:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:21:1: W293 blank line contains whitespace
backend/ssh_manager.py:30:1: W293 blank line contains whitespace
backend/ssh_manager.py:36:1: W293 blank line contains whitespace
backend/ssh_manager.py:40:1: W293 blank line contains whitespace
backend/ssh_manager.py:48:17: E722 do not use bare 'except'
backend/ssh_manager.py:52:21: E722 do not use bare 'except'
backend/ssh_manager.py:55:1: W293 blank line contains whitespace
backend/ssh_manager.py:59:1: W293 blank line contains whitespace
backend/ssh_manager.py:64:1: W293 blank line contains whitespace
backend/ssh_manager.py:67:1: W293 blank line contains whitespace
backend/ssh_manager.py:89:1: W293 blank line contains whitespace
backend/ssh_manager.py:92:1: W293 blank line contains whitespace
backend/ssh_manager.py:95:1: W293 blank line contains whitespace
backend/ssh_manager.py:99:1: W293 blank line contains whitespace
backend/ssh_manager.py:104:17: E722 do not use bare 'except'
backend/ssh_manager.py:107:1: W293 blank line contains whitespace
backend/ssh_manager.py:114:17: E722 do not use bare 'except'
backend/ssh_manager.py:117:1: W293 blank line contains whitespace
backend/ssh_manager.py:123:1: W293 blank line contains whitespace
backend/ssh_manager.py:132:1: W293 blank line contains whitespace
backend/ssh_manager.py:141:1: W293 blank line contains whitespace
backend/ssh_manager.py:145:9: E722 do not use bare 'except'
backend/ssh_manager.py:149:1: E305 expected 2 blank lines after class or function definition, found 1
backend/ssh_manager.py:151:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:157:1: W293 blank line contains whitespace
backend/ssh_manager.py:159:1: W293 blank line contains whitespace
backend/ssh_manager.py:163:1: W293 blank line contains whitespace
backend/ssh_manager.py:170:1: W293 blank line contains whitespace
backend/ssh_manager.py:177:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:183:1: W293 blank line contains whitespace
backend/ssh_manager.py:188:1: W293 blank line contains whitespace
backend/ssh_manager.py:192:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:198:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:206:1: W293 blank line contains whitespace
backend/ssh_manager.py:208:1: W293 blank line contains whitespace
backend/ssh_manager.py:217:1: W293 blank line contains whitespace
backend/ssh_manager.py:221:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:232:1: W293 blank line contains whitespace
backend/ssh_manager.py:235:1: W293 blank line contains whitespace
backend/ssh_manager.py:248:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:255:1: W293 blank line contains whitespace
backend/ssh_manager.py:257:1: W293 blank line contains whitespace
backend/ssh_manager.py:262:1: W293 blank line contains whitespace
backend/ssh_manager.py:266:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:273:1: W293 blank line contains whitespace
backend/ssh_manager.py:276:1: W293 blank line contains whitespace
backend/ssh_manager.py:279:1: W293 blank line contains whitespace
backend/ssh_manager.py:281:1: W293 blank line contains whitespace
backend/ssh_manager.py:285:1: W293 blank line contains whitespace
backend/ssh_manager.py:288:1: W293 blank line contains whitespace
backend/ssh_manager.py:295:1: W293 blank line contains whitespace
backend/ssh_manager.py:299:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:306:1: W293 blank line contains whitespace
backend/ssh_manager.py:307:9: F841 local variable 'result' is assigned to but never used
backend/ssh_manager.py:308:1: W293 blank line contains whitespace
backend/ssh_manager.py:311:1: W293 blank line contains whitespace
backend/ssh_manager.py:314:1: W293 blank line contains whitespace
backend/ssh_manager.py:319:1: W293 blank line contains whitespace
backend/ssh_manager.py:323:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:329:1: W293 blank line contains whitespace
backend/ssh_manager.py:331:1: W293 blank line contains whitespace
backend/ssh_manager.py:334:1: W293 blank line contains whitespace
backend/ssh_manager.py:337:1: W293 blank line contains whitespace
backend/ssh_manager.py:339:1: W293 blank line contains whitespace
backend/ssh_manager.py:341:1: W293 blank line contains whitespace
backend/ssh_manager.py:345:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:353:1: W293 blank line contains whitespace
backend/ssh_manager.py:358:1: W293 blank line contains whitespace
backend/ssh_manager.py:363:1: W293 blank line contains whitespace
backend/ssh_manager.py:366:1: W293 blank line contains whitespace
backend/ssh_manager.py:368:1: W293 blank line contains whitespace
backend/ssh_manager.py:373:1: W293 blank line contains whitespace
backend/ssh_manager.py:377:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:383:1: W293 blank line contains whitespace
backend/ssh_manager.py:389:1: W293 blank line contains whitespace
backend/ssh_manager.py:392:1: W293 blank line contains whitespace
backend/ssh_manager.py:394:1: W293 blank line contains whitespace
backend/ssh_manager.py:400:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:408:1: W293 blank line contains whitespace
backend/ssh_manager.py:410:21: F541 f-string is missing placeholders
backend/ssh_manager.py:412:1: W293 blank line contains whitespace
backend/ssh_manager.py:415:1: W293 blank line contains whitespace
backend/ssh_manager.py:418:1: W293 blank line contains whitespace
backend/ssh_manager.py:421:1: W293 blank line contains whitespace
backend/ssh_manager.py:438:1: W293 blank line contains whitespace
backend/ssh_manager.py:442:1: W293 blank line contains whitespace
backend/ssh_manager.py:445:1: W293 blank line contains whitespace
backend/ssh_manager.py:449:1: W293 blank line contains whitespace
backend/ssh_manager.py:452:1: W293 blank line contains whitespace
backend/ssh_manager.py:460:1: W293 blank line contains whitespace
backend/ssh_manager.py:464:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:472:1: W293 blank line contains whitespace
backend/ssh_manager.py:475:1: W293 blank line contains whitespace
backend/ssh_manager.py:477:1: W293 blank line contains whitespace
backend/ssh_manager.py:481:1: W293 blank line contains whitespace
backend/ssh_manager.py:483:1: W293 blank line contains whitespace
backend/ssh_manager.py:491:1: W293 blank line contains whitespace
backend/ssh_manager.py:495:1: W293 blank line contains whitespace
backend/ssh_manager.py:497:1: W293 blank line contains whitespace
backend/ssh_manager.py:506:1: W293 blank line contains whitespace
backend/ssh_manager.py:510:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:518:1: W293 blank line contains whitespace
backend/ssh_manager.py:522:1: W293 blank line contains whitespace
backend/ssh_manager.py:526:1: W293 blank line contains whitespace
backend/ssh_manager.py:530:1: W293 blank line contains whitespace
backend/ssh_manager.py:533:1: W293 blank line contains whitespace
backend/ssh_manager.py:535:1: W293 blank line contains whitespace
backend/ssh_manager.py:541:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:549:1: W293 blank line contains whitespace
backend/ssh_manager.py:552:1: W293 blank line contains whitespace
backend/ssh_manager.py:554:1: W293 blank line contains whitespace
backend/ssh_manager.py:569:1: W293 blank line contains whitespace
backend/ssh_manager.py:572:1: W293 blank line contains whitespace
backend/ssh_manager.py:581:1: W293 blank line contains whitespace
backend/ssh_manager.py:585:1: E302 expected 2 blank lines, found 1
backend/ssh_manager.py:592:1: W293 blank line contains whitespace
backend/ssh_manager.py:599:1: W293 blank line contains whitespace
backend/ssh_manager.py:601:1: W293 blank line contains whitespace
backend/ssh_manager.py:605:1: E305 expected 2 blank lines after class or function definition, found 1
backend/ssh_manager.py:608:1: W293 blank line contains whitespace
backend/ssh_manager.py:612:1: W293 blank line contains whitespace
backend/startup_validation.py:27:1: W293 blank line contains whitespace
backend/startup_validation.py:32:1: W293 blank line contains whitespace
backend/startup_validation.py:35:1: W293 blank line contains whitespace
backend/startup_validation.py:40:1: W293 blank line contains whitespace
backend/startup_validation.py:48:1: W293 blank line contains whitespace
backend/startup_validation.py:55:1: W293 blank line contains whitespace
backend/startup_validation.py:62:1: W293 blank line contains whitespace
backend/startup_validation.py:69:1: W293 blank line contains whitespace
backend/startup_validation.py:80:1: W293 blank line contains whitespace
backend/startup_validation.py:83:1: W293 blank line contains whitespace
backend/startup_validation.py:90:1: W293 blank line contains whitespace
backend/startup_validation.py:97:1: W293 blank line contains whitespace
backend/startup_validation.py:105:1: W293 blank line contains whitespace
backend/startup_validation.py:115:1: W293 blank line contains whitespace
backend/startup_validation.py:119:1: W293 blank line contains whitespace
backend/startup_validation.py:123:1: W293 blank line contains whitespace
backend/startup_validation.py:130:1: W293 blank line contains whitespace
backend/startup_validation.py:135:1: W293 blank line contains whitespace
backend/task_policy.py:10:1: F401 'typing.List' imported but unused
backend/task_policy.py:29:1: W293 blank line contains whitespace
backend/task_policy.py:36:1: W293 blank line contains whitespace
backend/task_policy.py:43:1: W293 blank line contains whitespace
backend/task_policy.py:48:1: W293 blank line contains whitespace
backend/task_policy.py:55:1: W293 blank line contains whitespace
backend/task_policy.py:60:1: W293 blank line contains whitespace
backend/task_policy.py:64:1: W293 blank line contains whitespace
backend/task_policy.py:112:1: W293 blank line contains whitespace
backend/task_policy.py:116:1: W293 blank line contains whitespace
backend/task_policy.py:121:1: W293 blank line contains whitespace
backend/task_policy.py:127:1: W293 blank line contains whitespace
backend/task_policy.py:131:1: W293 blank line contains whitespace
backend/task_policy.py:134:1: W293 blank line contains whitespace
backend/task_policy.py:137:1: W293 blank line contains whitespace
backend/task_policy.py:144:1: W293 blank line contains whitespace
backend/task_policy.py:146:1: W293 blank line contains whitespace
backend/task_policy.py:152:1: W293 blank line contains whitespace
backend/task_policy.py:153:27: F541 f-string is missing placeholders
backend/task_policy.py:154:1: W293 blank line contains whitespace
backend/task_policy.py:160:1: W293 blank line contains whitespace
backend/task_policy.py:162:1: W293 blank line contains whitespace
backend/task_policy.py:166:1: W293 blank line contains whitespace
backend/task_policy.py:170:1: W293 blank line contains whitespace
backend/task_policy.py:173:1: W293 blank line contains whitespace
backend/task_policy.py:178:1: W293 blank line contains whitespace
backend/task_policy.py:181:1: W293 blank line contains whitespace
backend/task_policy.py:183:1: W293 blank line contains whitespace
backend/task_policy.py:187:1: W293 blank line contains whitespace
backend/task_policy.py:202:1: E302 expected 2 blank lines, found 1
backend/task_policy.py:213:1: W293 blank line contains whitespace
backend/task_policy.py:216:1: W293 blank line contains whitespace
backend/task_policy.py:227:1: W293 blank line contains whitespace
backend/task_policy.py:230:1: W293 blank line contains whitespace
backend/task_policy.py:239:1: W293 blank line contains whitespace
backend/task_policy.py:247:1: W293 blank line contains whitespace
backend/task_policy.py:255:1: W293 blank line contains whitespace
backend/task_recovery.py:15:1: E402 module level import not at top of file
backend/task_recovery.py:16:1: E402 module level import not at top of file
backend/task_recovery.py:32:1: W293 blank line contains whitespace
backend/task_recovery.py:37:1: W293 blank line contains whitespace
backend/task_recovery.py:41:48: W291 trailing whitespace
backend/task_recovery.py:43:1: W293 blank line contains whitespace
backend/task_recovery.py:47:1: W293 blank line contains whitespace
backend/task_recovery.py:50:1: W293 blank line contains whitespace
backend/task_recovery.py:57:1: W293 blank line contains whitespace
backend/task_recovery.py:62:1: W293 blank line contains whitespace
backend/task_recovery.py:66:1: W293 blank line contains whitespace
backend/task_recovery.py:77:1: W293 blank line contains whitespace
backend/task_recovery.py:85:1: W293 blank line contains whitespace
backend/task_recovery.py:87:1: W293 blank line contains whitespace
backend/task_recovery.py:94:1: W293 blank line contains whitespace
backend/task_recovery.py:101:1: W293 blank line contains whitespace
backend/task_recovery.py:119:1: W293 blank line contains whitespace
backend/task_recovery.py:126:1: W293 blank line contains whitespace
backend/task_recovery.py:132:1: W293 blank line contains whitespace
backend/task_recovery.py:146:1: W293 blank line contains whitespace
backend/task_recovery.py:151:1: W293 blank line contains whitespace
backend/task_recovery.py:155:1: W293 blank line contains whitespace
backend/task_recovery.py:162:1: W293 blank line contains whitespace
backend/task_recovery.py:168:1: W293 blank line contains whitespace
backend/task_recovery.py:176:1: W293 blank line contains whitespace
backend/task_recovery.py:178:1: W293 blank line contains whitespace
backend/task_recovery.py:185:1: W293 blank line contains whitespace
backend/task_recovery.py:191:1: W293 blank line contains whitespace
backend/task_recovery.py:197:1: W293 blank line contains whitespace
backend/task_recovery.py:212:1: W293 blank line contains whitespace
backend/task_recovery.py:217:1: W293 blank line contains whitespace
backend/task_recovery.py:220:1: W293 blank line contains whitespace
backend/task_recovery.py:222:1: W293 blank line contains whitespace
backend/task_recovery.py:229:1: W293 blank line contains whitespace
backend/task_recovery.py:241:11: F541 f-string is missing placeholders
backend/task_runner.py:19:1: E402 module level import not at top of file
backend/task_runner.py:20:1: E402 module level import not at top of file
backend/task_runner.py:21:1: E402 module level import not at top of file
backend/task_runner.py:46:1: W293 blank line contains whitespace
backend/task_runner.py:52:1: W293 blank line contains whitespace
backend/task_runner.py:60:1: W293 blank line contains whitespace
backend/task_runner.py:66:1: W293 blank line contains whitespace
backend/task_runner.py:70:1: W293 blank line contains whitespace
backend/task_runner.py:73:1: W293 blank line contains whitespace
backend/task_runner.py:88:1: W293 blank line contains whitespace
backend/task_runner.py:96:1: W293 blank line contains whitespace
backend/task_runner.py:117:1: W293 blank line contains whitespace
backend/task_runner.py:135:17: E722 do not use bare 'except'
backend/task_runner.py:137:1: W293 blank line contains whitespace
backend/task_runner.py:141:1: W293 blank line contains whitespace
backend/task_runner.py:147:1: W293 blank line contains whitespace
backend/task_runner.py:148:5: C901 'TaskRunner._execute_ssh_command' is too complex (19)
backend/task_runner.py:151:1: W293 blank line contains whitespace
backend/task_runner.py:159:1: W293 blank line contains whitespace
backend/task_runner.py:169:1: W293 blank line contains whitespace
backend/task_runner.py:176:1: W293 blank line contains whitespace
backend/task_runner.py:184:29: E722 do not use bare 'except'
backend/task_runner.py:186:1: W293 blank line contains whitespace
backend/task_runner.py:191:1: W293 blank line contains whitespace
backend/task_runner.py:197:1: W293 blank line contains whitespace
backend/task_runner.py:204:1: W293 blank line contains whitespace
backend/task_runner.py:207:1: W293 blank line contains whitespace
backend/task_runner.py:214:1: W293 blank line contains whitespace
backend/task_runner.py:219:1: W293 blank line contains whitespace
backend/task_runner.py:221:1: W293 blank line contains whitespace
backend/task_runner.py:229:9: F841 local variable 'e' is assigned to but never used
backend/task_runner.py:229:16: F821 undefined name 'socket'
backend/task_runner.py:234:1: W293 blank line contains whitespace
backend/task_runner.py:239:1: W293 blank line contains whitespace
backend/task_runner.py:244:1: W293 blank line contains whitespace
backend/task_runner.py:246:1: W293 blank line contains whitespace
backend/task_runner.py:258:1: W293 blank line contains whitespace
backend/task_runner.py:271:1: W293 blank line contains whitespace
backend/task_runner.py:274:1: W293 blank line contains whitespace
backend/task_runner.py:280:1: W293 blank line contains whitespace
backend/task_runner.py:284:1: W293 blank line contains whitespace
backend/task_runner.py:292:1: W293 blank line contains whitespace
backend/task_runner.py:295:1: W293 blank line contains whitespace
backend/task_runner.py:299:1: W293 blank line contains whitespace
backend/task_runner.py:304:1: W293 blank line contains whitespace
backend/task_runner.py:306:1: W293 blank line contains whitespace
backend/task_runner.py:317:1: E302 expected 2 blank lines, found 1
backend/task_runner.py:329:1: W293 blank line contains whitespace
backend/telegram_bot.py:9:1: F401 'sys' imported but unused
backend/telegram_bot.py:49:1: W293 blank line contains whitespace
backend/telegram_bot.py:52:1: W293 blank line contains whitespace
backend/telegram_bot.py:55:1: W293 blank line contains whitespace
backend/telegram_bot.py:58:1: W293 blank line contains whitespace
backend/telegram_bot.py:64:1: W293 blank line contains whitespace
backend/telegram_bot.py:73:1: W293 blank line contains whitespace
backend/telegram_bot.py:79:1: W293 blank line contains whitespace
backend/telegram_bot.py:86:1: W293 blank line contains whitespace
backend/telegram_bot.py:105:1: W293 blank line contains whitespace
backend/telegram_bot.py:108:1: W293 blank line contains whitespace
backend/telegram_bot.py:116:1: W293 blank line contains whitespace
backend/telegram_bot.py:124:1: W293 blank line contains whitespace
backend/telegram_bot.py:127:1: W293 blank line contains whitespace
backend/telegram_bot.py:129:1: W293 blank line contains whitespace
backend/telegram_bot.py:136:1: W293 blank line contains whitespace
backend/telegram_bot.py:139:15: F541 f-string is missing placeholders
backend/telegram_bot.py:146:1: W391 blank line at end of file
backend/terminal.py:16:1: F401 'threading' imported but unused
backend/terminal.py:19:1: F401 'select' imported but unused
backend/terminal.py:21:1: F401 'tempfile' imported but unused
backend/terminal.py:23:1: F401 'uuid' imported but unused
backend/terminal.py:29:1: E402 module level import not at top of file
backend/terminal.py:30:1: E402 module level import not at top of file
backend/terminal.py:31:1: E402 module level import not at top of file
backend/terminal.py:45:1: E302 expected 2 blank lines, found 1
backend/terminal.py:48:1: W293 blank line contains whitespace
backend/terminal.py:56:1: W293 blank line contains whitespace
backend/terminal.py:68:1: W293 blank line contains whitespace
backend/terminal.py:69:5: C901 'SSHTerminalSession.connect' is too complex (17)
backend/terminal.py:74:1: W293 blank line contains whitespace
backend/terminal.py:77:29: E128 continuation line under-indented for visual indent
backend/terminal.py:78:29: E128 continuation line under-indented for visual indent
backend/terminal.py:79:29: E128 continuation line under-indented for visual indent
backend/terminal.py:82:1: W293 blank line contains whitespace
backend/terminal.py:84:24: E128 continuation line under-indented for visual indent
backend/terminal.py:85:24: E128 continuation line under-indented for visual indent
backend/terminal.py:86:24: E128 continuation line under-indented for visual indent
backend/terminal.py:87:24: E128 continuation line under-indented for visual indent
backend/terminal.py:88:24: E128 continuation line under-indented for visual indent
backend/terminal.py:89:1: W293 blank line contains whitespace
backend/terminal.py:93:1: W293 blank line contains whitespace
backend/terminal.py:103:1: W293 blank line contains whitespace
backend/terminal.py:112:1: W293 blank line contains whitespace
backend/terminal.py:120:29: E722 do not use bare 'except'
backend/terminal.py:122:1: W293 blank line contains whitespace
backend/terminal.py:134:1: W293 blank line contains whitespace
backend/terminal.py:143:1: W293 blank line contains whitespace
backend/terminal.py:147:1: W293 blank line contains whitespace
backend/terminal.py:151:1: W293 blank line contains whitespace
backend/terminal.py:154:1: W293 blank line contains whitespace
backend/terminal.py:161:1: W293 blank line contains whitespace
backend/terminal.py:164:1: W293 blank line contains whitespace
backend/terminal.py:178:1: W293 blank line contains whitespace
backend/terminal.py:180:24: E128 continuation line under-indented for visual indent
backend/terminal.py:181:24: E128 continuation line under-indented for visual indent
backend/terminal.py:182:24: E128 continuation line under-indented for visual indent
backend/terminal.py:183:24: E128 continuation line under-indented for visual indent
backend/terminal.py:184:1: W293 blank line contains whitespace
backend/terminal.py:187:1: W293 blank line contains whitespace
backend/terminal.py:194:1: W293 blank line contains whitespace
backend/terminal.py:196:1: W293 blank line contains whitespace
backend/terminal.py:199:27: E128 continuation line under-indented for visual indent
backend/terminal.py:200:27: E128 continuation line under-indented for visual indent
backend/terminal.py:201:27: E128 continuation line under-indented for visual indent
backend/terminal.py:206:25: E128 continuation line under-indented for visual indent
backend/terminal.py:207:25: E128 continuation line under-indented for visual indent
backend/terminal.py:208:25: E128 continuation line under-indented for visual indent
backend/terminal.py:209:25: E128 continuation line under-indented for visual indent
backend/terminal.py:212:1: W293 blank line contains whitespace
backend/terminal.py:217:9: E722 do not use bare 'except'
backend/terminal.py:219:1: W293 blank line contains whitespace
backend/terminal.py:223:1: W293 blank line contains whitespace
backend/terminal.py:227:1: W293 blank line contains whitespace
backend/terminal.py:233:13: E722 do not use bare 'except'
backend/terminal.py:235:1: W293 blank line contains whitespace
backend/terminal.py:238:9: F841 local variable 'loop' is assigned to but never used
backend/terminal.py:239:1: W293 blank line contains whitespace
backend/terminal.py:249:1: W293 blank line contains whitespace
backend/terminal.py:254:1: W293 blank line contains whitespace
backend/terminal.py:259:1: W293 blank line contains whitespace
backend/terminal.py:260:5: F811 redefinition of unused 'handle_input' from line 228
backend/terminal.py:269:13: E722 do not use bare 'except'
backend/terminal.py:271:1: W293 blank line contains whitespace
backend/terminal.py:278:28: E128 continuation line under-indented for visual indent
backend/terminal.py:279:28: E128 continuation line under-indented for visual indent
backend/terminal.py:280:28: E128 continuation line under-indented for visual indent
backend/terminal.py:281:28: E128 continuation line under-indented for visual indent
backend/terminal.py:284:1: W293 blank line contains whitespace
backend/terminal.py:290:13: E722 do not use bare 'except'
backend/terminal.py:292:1: W293 blank line contains whitespace
backend/terminal.py:297:1: W293 blank line contains whitespace
backend/terminal.py:300:1: W293 blank line contains whitespace
backend/terminal.py:303:1: W293 blank line contains whitespace
backend/terminal.py:305:20: E128 continuation line under-indented for visual indent
backend/terminal.py:306:20: E128 continuation line under-indented for visual indent
backend/terminal.py:307:20: E128 continuation line under-indented for visual indent
backend/terminal.py:308:20: E128 continuation line under-indented for visual indent
backend/terminal.py:309:20: E128 continuation line under-indented for visual indent
backend/terminal.py:310:1: W293 blank line contains whitespace
backend/terminal.py:314:1: W293 blank line contains whitespace
backend/terminal.py:320:9: E722 do not use bare 'except'
backend/terminal.py:322:1: W293 blank line contains whitespace
backend/terminal.py:328:9: E722 do not use bare 'except'
backend/terminal.py:330:1: W293 blank line contains whitespace
backend/terminal.py:337:1: E305 expected 2 blank lines after class or function definition, found 1
backend/terminal.py:339:1: C901 'handle_terminal' is too complex (17)
backend/terminal.py:339:1: E302 expected 2 blank lines, found 1
backend/terminal.py:343:1: W293 blank line contains whitespace
backend/terminal.py:348:1: W293 blank line contains whitespace
backend/terminal.py:352:1: W293 blank line contains whitespace
backend/terminal.py:355:27: E128 continuation line under-indented for visual indent
backend/terminal.py:361:1: W293 blank line contains whitespace
backend/terminal.py:364:1: W293 blank line contains whitespace
backend/terminal.py:367:27: E128 continuation line under-indented for visual indent
backend/terminal.py:373:1: W293 blank line contains whitespace
backend/terminal.py:378:27: E128 continuation line under-indented for visual indent
backend/terminal.py:379:27: E128 continuation line under-indented for visual indent
backend/terminal.py:385:1: W293 blank line contains whitespace
backend/terminal.py:389:1: W293 blank line contains whitespace
backend/terminal.py:397:1: W293 blank line contains whitespace
backend/terminal.py:400:1: W293 blank line contains whitespace
backend/terminal.py:407:1: W293 blank line contains whitespace
backend/terminal.py:414:1: W293 blank line contains whitespace
backend/terminal.py:416:1: W293 blank line contains whitespace
backend/terminal.py:431:1: W293 blank line contains whitespace
backend/terminal.py:441:1: W293 blank line contains whitespace
backend/terminal.py:445:1: W293 blank line contains whitespace
backend/terminal.py:448:1: W293 blank line contains whitespace
backend/terminal.py:454:1: W293 blank line contains whitespace
backend/terminal.py:458:1: W293 blank line contains whitespace
backend/terminal.py:464:1: W293 blank line contains whitespace
backend/terminal.py:468:1: W293 blank line contains whitespace
backend/terminal.py:471:1: W293 blank line contains whitespace
backend/terminal.py:474:1: W293 blank line contains whitespace
backend/terminal.py:477:1: W293 blank line contains whitespace
backend/terminal.py:480:1: W293 blank line contains whitespace
backend/terminal.py:485:1: W293 blank line contains whitespace
backend/terminal.py:498:1: W293 blank line contains whitespace
backend/terminal.py:502:1: E302 expected 2 blank lines, found 1
backend/terminal.py:505:1: W293 blank line contains whitespace
backend/terminal.py:508:1: W293 blank line contains whitespace
backend/terminal.py:510:16: E128 continuation line under-indented for visual indent
backend/terminal.py:511:16: E128 continuation line under-indented for visual indent
backend/terminal.py:512:16: E128 continuation line under-indented for visual indent
backend/terminal.py:513:1: W293 blank line contains whitespace
backend/terminal.py:514:11: F541 f-string is missing placeholders
backend/terminal.py:515:11: F541 f-string is missing placeholders
backend/terminal.py:516:11: F541 f-string is missing placeholders
backend/terminal.py:518:11: F541 f-string is missing placeholders
backend/terminal.py:520:11: F541 f-string is missing placeholders
backend/terminal.py:522:11: F541 f-string is missing placeholders
backend/terminal.py:523:11: F541 f-string is missing placeholders
backend/terminal.py:524:11: F541 f-string is missing placeholders
backend/terminal.py:525:11: F541 f-string is missing placeholders
backend/terminal.py:526:1: W293 blank line contains whitespace
backend/terminal.py:538:5: F824 `global ws_server` is unused: name is never assigned in scope
backend/terminal.py:539:1: W293 blank line contains whitespace
backend/terminal.py:541:11: F541 f-string is missing placeholders
backend/terminal.py:542:1: W293 blank line contains whitespace
backend/terminal.py:555:1: W293 blank line contains whitespace
backend/terminal.py:557:1: W293 blank line contains whitespace
backend/terminal.py:562:1: W293 blank line contains whitespace
backend/terminal.py:565:1: W293 blank line contains whitespace
backend/terminal.py:576:1: W293 blank line contains whitespace
backend/terminal.py:579:1: W293 blank line contains whitespace
backend/user_management.py:39:1: E302 expected 2 blank lines, found 1
backend/user_management.py:46:1: W293 blank line contains whitespace
backend/user_management.py:51:1: W293 blank line contains whitespace
backend/user_management.py:56:1: W293 blank line contains whitespace
backend/user_management.py:62:1: W293 blank line contains whitespace
backend/user_management.py:80:1: W293 blank line contains whitespace
backend/user_management.py:117:1: W293 blank line contains whitespace
backend/user_management.py:124:1: W293 blank line contains whitespace
backend/user_management.py:130:1: W293 blank line contains whitespace
backend/user_management.py:136:1: W293 blank line contains whitespace
backend/user_management.py:143:9: E722 do not use bare 'except'
backend/user_management.py:145:1: W293 blank line contains whitespace
backend/user_management.py:150:1: W293 blank line contains whitespace
backend/user_management.py:155:1: W293 blank line contains whitespace
backend/user_management.py:167:1: W293 blank line contains whitespace
backend/user_management.py:168:88: W291 trailing whitespace
backend/user_management.py:169:20: E128 continuation line under-indented for visual indent
backend/user_management.py:177:1: W293 blank line contains whitespace
backend/user_management.py:180:1: W293 blank line contains whitespace
backend/user_management.py:184:1: W293 blank line contains whitespace
backend/user_management.py:187:1: W293 blank line contains whitespace
backend/user_management.py:191:1: W293 blank line contains whitespace
backend/user_management.py:197:1: W293 blank line contains whitespace
backend/user_management.py:203:1: W293 blank line contains whitespace
backend/user_management.py:207:1: W293 blank line contains whitespace
backend/user_management.py:209:85: W291 trailing whitespace
backend/user_management.py:213:1: W293 blank line contains whitespace
backend/user_management.py:217:1: W293 blank line contains whitespace
backend/user_management.py:219:1: W293 blank line contains whitespace
backend/user_management.py:222:1: W293 blank line contains whitespace
backend/user_management.py:231:1: W293 blank line contains whitespace
backend/user_management.py:233:77: W291 trailing whitespace
backend/user_management.py:235:27: W291 trailing whitespace
backend/user_management.py:238:1: W293 blank line contains whitespace
backend/user_management.py:240:1: W293 blank line contains whitespace
backend/user_management.py:244:1: W293 blank line contains whitespace
backend/user_management.py:248:1: W293 blank line contains whitespace
backend/user_management.py:252:1: W293 blank line contains whitespace
backend/user_management.py:258:1: W293 blank line contains whitespace
backend/user_management.py:268:1: W293 blank line contains whitespace
backend/user_management.py:270:1: W293 blank line contains whitespace
backend/user_management.py:273:1: W293 blank line contains whitespace
backend/user_management.py:279:1: W293 blank line contains whitespace
backend/user_management.py:281:73: W291 trailing whitespace
backend/user_management.py:283:27: W291 trailing whitespace
backend/user_management.py:286:1: W293 blank line contains whitespace
backend/user_management.py:289:1: W293 blank line contains whitespace
backend/user_management.py:292:1: W293 blank line contains whitespace
backend/user_management.py:305:1: W293 blank line contains whitespace
backend/user_management.py:309:1: W293 blank line contains whitespace
backend/user_management.py:315:1: W293 blank line contains whitespace
backend/user_management.py:317:73: W291 trailing whitespace
backend/user_management.py:319:27: W291 trailing whitespace
backend/user_management.py:322:1: W293 blank line contains whitespace
backend/user_management.py:336:1: W293 blank line contains whitespace
backend/user_management.py:339:1: W293 blank line contains whitespace
backend/user_management.py:343:1: W293 blank line contains whitespace
backend/user_management.py:351:1: W293 blank line contains whitespace
backend/user_management.py:354:1: W293 blank line contains whitespace
backend/user_management.py:358:1: W293 blank line contains whitespace
backend/user_management.py:362:1: W293 blank line contains whitespace
backend/user_management.py:366:1: W293 blank line contains whitespace
backend/user_management.py:372:1: W293 blank line contains whitespace
backend/user_management.py:376:1: W293 blank line contains whitespace
backend/user_management.py:380:1: W293 blank line contains whitespace
backend/user_management.py:382:1: W293 blank line contains whitespace
backend/user_management.py:385:1: W293 blank line contains whitespace
backend/user_management.py:392:1: W293 blank line contains whitespace
backend/user_management.py:396:1: W293 blank line contains whitespace
backend/user_management.py:399:1: W293 blank line contains whitespace
backend/user_management.py:403:1: W293 blank line contains whitespace
backend/user_management.py:408:1: W293 blank line contains whitespace
backend/user_management.py:414:1: W293 blank line contains whitespace
backend/user_management.py:416:1: W293 blank line contains whitespace
backend/user_management.py:419:1: W293 blank line contains whitespace
backend/user_management.py:425:1: W293 blank line contains whitespace
backend/user_management.py:429:1: W293 blank line contains whitespace
backend/user_management.py:433:1: W293 blank line contains whitespace
backend/user_management.py:440:1: W293 blank line contains whitespace
backend/user_management.py:444:1: W293 blank line contains whitespace
backend/user_management.py:446:1: W293 blank line contains whitespace
backend/user_management.py:449:1: W293 blank line contains whitespace
backend/user_management.py:455:1: W293 blank line contains whitespace
backend/user_management.py:457:1: W293 blank line contains whitespace
backend/user_management.py:461:1: W293 blank line contains whitespace
backend/user_management.py:467:1: W293 blank line contains whitespace
backend/user_management.py:476:1: E302 expected 2 blank lines, found 1
backend/webhook_dispatcher.py:10:1: F401 'json' imported but unused
backend/webhook_dispatcher.py:23:1: E402 module level import not at top of file
backend/webhook_dispatcher.py:24:1: E402 module level import not at top of file
backend/webhook_dispatcher.py:25:1: E402 module level import not at top of file
backend/webhook_dispatcher.py:34:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:37:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:43:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:47:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:51:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:53:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:63:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:66:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:70:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:74:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:78:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:82:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:86:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:96:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:99:35: F541 f-string is missing placeholders
backend/webhook_dispatcher.py:100:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:102:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:110:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:113:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:119:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:123:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:125:21: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:126:21: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:127:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:135:36: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:136:36: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:137:36: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:139:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:142:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:145:28: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:146:28: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:147:28: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:148:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:152:21: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:153:21: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:159:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:166:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:171:21: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:172:21: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:173:21: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:174:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:185:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:189:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:199:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:207:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:210:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:217:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:221:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:229:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:240:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:243:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:245:27: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:246:27: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:247:27: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:248:27: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:249:27: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:251:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:257:13: E722 do not use bare 'except'
backend/webhook_dispatcher.py:259:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:271:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:275:30: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:276:30: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:277:30: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:278:30: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:280:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:282:26: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:283:26: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:284:26: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:285:26: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:286:26: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:287:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:290:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:301:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:303:26: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:304:26: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:305:26: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:306:26: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:307:26: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:308:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:313:25: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:314:25: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:316:1: W293 blank line contains whitespace
backend/webhook_dispatcher.py:319:17: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:320:17: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:321:17: E128 continuation line under-indented for visual indent
backend/webhook_dispatcher.py:322:17: E128 continuation line under-indented for visual indent
backend/websocket_server.py:19:1: E402 module level import not at top of file
backend/websocket_server.py:20:1: E402 module level import not at top of file
backend/websocket_server.py:21:1: E402 module level import not at top of file
backend/websocket_server.py:44:1: C901 'broadcast_server_stats' is too complex (16)
backend/websocket_server.py:44:1: E302 expected 2 blank lines, found 1
backend/websocket_server.py:52:1: W293 blank line contains whitespace
backend/websocket_server.py:56:1: W293 blank line contains whitespace
backend/websocket_server.py:59:1: W293 blank line contains whitespace
backend/websocket_server.py:62:1: W293 blank line contains whitespace
backend/websocket_server.py:66:1: W293 blank line contains whitespace
backend/websocket_server.py:72:1: W293 blank line contains whitespace
backend/websocket_server.py:82:1: W293 blank line contains whitespace
backend/websocket_server.py:90:1: W293 blank line contains whitespace
backend/websocket_server.py:92:1: W293 blank line contains whitespace
backend/websocket_server.py:95:1: W293 blank line contains whitespace
backend/websocket_server.py:105:1: W293 blank line contains whitespace
backend/websocket_server.py:108:1: W293 blank line contains whitespace
backend/websocket_server.py:118:1: W293 blank line contains whitespace
backend/websocket_server.py:126:1: W293 blank line contains whitespace
backend/websocket_server.py:138:1: W293 blank line contains whitespace
backend/websocket_server.py:142:1: W293 blank line contains whitespace
backend/websocket_server.py:145:1: W293 blank line contains whitespace
backend/websocket_server.py:155:1: W293 blank line contains whitespace
backend/websocket_server.py:157:16: E128 continuation line under-indented for visual indent
backend/websocket_server.py:158:16: E128 continuation line under-indented for visual indent
backend/websocket_server.py:159:1: W293 blank line contains whitespace
backend/websocket_server.py:164:1: W293 blank line contains whitespace
backend/websocket_server.py:167:1: W293 blank line contains whitespace
backend/websocket_server.py:170:1: W293 blank line contains whitespace
backend/websocket_server.py:181:1: W293 blank line contains whitespace
backend/websocket_server.py:186:1: W293 blank line contains whitespace
backend/websocket_server.py:194:1: W293 blank line contains whitespace
backend/websocket_server.py:199:1: W293 blank line contains whitespace
backend/websocket_server.py:202:21: F841 local variable 'server_ids' is assigned to but never used
backend/websocket_server.py:205:1: W293 blank line contains whitespace
backend/websocket_server.py:215:1: W293 blank line contains whitespace
backend/websocket_server.py:218:20: E128 continuation line under-indented for visual indent
backend/websocket_server.py:222:21: E128 continuation line under-indented for visual indent
backend/websocket_server.py:223:21: E128 continuation line under-indented for visual indent
backend/websocket_server.py:230:1: W293 blank line contains whitespace
backend/websocket_server.py:233:1: W293 blank line contains whitespace
backend/websocket_server.py:235:20: E128 continuation line under-indented for visual indent
backend/websocket_server.py:236:20: E128 continuation line under-indented for visual indent
backend/websocket_server.py:246:1: W293 blank line contains whitespace
backend/websocket_server.py:249:1: W293 blank line contains whitespace
backend/websocket_server.py:250:15: F541 f-string is missing placeholders
backend/websocket_server.py:255:15: F541 f-string is missing placeholders
backend/websocket_server.py:262:5: F824 `global ws_server` is unused: name is never assigned in scope
backend/websocket_server.py:263:1: W293 blank line contains whitespace
backend/websocket_server.py:266:1: W293 blank line contains whitespace
backend/websocket_server.py:268:16: E128 continuation line under-indented for visual indent
backend/websocket_server.py:269:16: E128 continuation line under-indented for visual indent
backend/websocket_server.py:270:16: E128 continuation line under-indented for visual indent
backend/websocket_server.py:271:1: W293 blank line contains whitespace
backend/websocket_server.py:273:11: F541 f-string is missing placeholders
backend/websocket_server.py:279:1: W293 blank line contains whitespace
backend/websocket_server.py:281:1: W293 blank line contains whitespace
backend/websocket_server.py:286:1: W293 blank line contains whitespace
backend/websocket_server.py:301:5: F824 `global ws_server` is unused: name is never assigned in scope
backend/websocket_server.py:302:1: W293 blank line contains whitespace
backend/websocket_server.py:304:11: F541 f-string is missing placeholders
backend/websocket_server.py:305:1: W293 blank line contains whitespace
backend/websocket_server.py:314:1: W293 blank line contains whitespace
backend/websocket_server.py:316:1: W293 blank line contains whitespace
backend/websocket_server.py:322:1: W293 blank line contains whitespace
backend/websocket_server.py:325:1: W293 blank line contains whitespace
backend/websocket_server.py:336:1: W293 blank line contains whitespace
backend/websocket_server.py:339:1: W293 blank line contains whitespace
8     C901 'CentralAPIHandler.do_GET' is too complex (201)
1     E127 continuation line over-indented for visual indent
150   E128 continuation line under-indented for visual indent
1     E129 visually indented line with same indent as next logical line
165   E302 expected 2 blank lines, found 1
1     E303 too many blank lines (2)
9     E305 expected 2 blank lines after class or function definition, found 1
48    E402 module level import not at top of file
1     E501 line too long (155 > 150 characters)
2     E502 the backslash is redundant between brackets
1     E713 test for membership should be 'not in'
37    E722 do not use bare 'except'
25    F401 'datetime.datetime' imported but unused
80    F541 f-string is missing placeholders
2     F811 redefinition of unused 'Path' from line 15
4     F821 undefined name 'get_db'
1     F823 local variable 'metrics' defined in enclosing scope on line 52 referenced before assignment
4     F824 `global http_server` is unused: name is never assigned in scope
6     F841 local variable 'e' is assigned to but never used
113   W291 trailing whitespace
2384  W293 blank line contains whitespace
2     W391 blank line at end of file
3045
```

**Security Scanning (bandit):** See security scan results

**Frontend Linting (ESLint):** ⚠️ UNKNOWN

**TypeScript Type Check:** ⚠️ UNKNOWN

### 2. Unit & Integration Tests

**Result:** ⚠️ UNKNOWN

#### Test Summary:
```
=== Running All Tests ===
============================= test session starts ==============================
platform linux -- Python 3.11.14, pytest-9.0.2, pluggy-1.6.0 -- /opt/hostedtoolcache/Python/3.11.14/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/server-monitor/server-monitor
configfile: pyproject.toml
collecting ... collected 123 items

test_api.py::TestAuthentication::test_login_success ERROR                [  0%]
test_api.py::TestAuthentication::test_login_invalid_credentials ERROR    [  1%]
test_api.py::TestAuthentication::test_login_missing_fields ERROR         [  2%]
test_api.py::TestAuthentication::test_verify_token ERROR                 [  3%]
test_api.py::TestAuthentication::test_verify_invalid_token ERROR         [  4%]
test_api.py::TestServerCRUD::test_create_server ERROR                    [  4%]
test_api.py::TestServerCRUD::test_list_servers ERROR                     [  5%]
test_api.py::TestServerCRUD::test_get_server_by_id ERROR                 [  6%]
test_api.py::TestServerCRUD::test_update_server ERROR                    [  7%]
test_api.py::TestServerCRUD::test_delete_server ERROR                    [  8%]
test_api.py::TestStatistics::test_get_overview_stats ERROR               [  8%]
test_api.py::TestExport::test_export_servers_csv ERROR                   [  9%]
test_api.py::TestExport::test_export_servers_json ERROR                  [ 10%]
test_api.py::TestEmailConfig::test_get_email_config ERROR                [ 11%]
test_api.py::TestEmailConfig::test_update_email_config ERROR             [ 12%]
test_api.py::TestUnauthorizedAccess::test_list_servers_no_auth ERROR     [ 13%]
test_api.py::TestUnauthorizedAccess::test_create_server_no_auth ERROR    [ 13%]
test_api.py::TestUnauthorizedAccess::test_delete_server_no_auth ERROR    [ 14%]
test_api.py::test_summary ERROR                                          [ 15%]
test_cache.py::TestSimpleCache::test_clear PASSED                        [ 16%]
test_cache.py::TestSimpleCache::test_complex_data_types PASSED           [ 17%]
test_cache.py::TestSimpleCache::test_delete PASSED                       [ 17%]
test_cache.py::TestSimpleCache::test_get_nonexistent_key PASSED          [ 18%]
test_cache.py::TestSimpleCache::test_get_or_compute_cache_hit PASSED     [ 19%]
test_cache.py::TestSimpleCache::test_get_or_compute_cache_miss PASSED    [ 20%]
test_cache.py::TestSimpleCache::test_sanitize_key PASSED                 [ 21%]
test_cache.py::TestSimpleCache::test_set_and_get PASSED                  [ 21%]
test_cache.py::TestSimpleCache::test_stats_tracking PASSED               [ 22%]
test_cache.py::TestSimpleCache::test_ttl_expiration PASSED               [ 23%]
test_cache.py::TestCacheSingleton::test_get_cache_singleton PASSED       [ 24%]
test_crypto_vault.py::TestCryptoVault::test_encrypt_decrypt_roundtrip PASSED [ 25%]
test_crypto_vault.py::TestCryptoVault::test_wrong_key_fails PASSED       [ 26%]
test_crypto_vault.py::TestCryptoVault::test_tampered_ciphertext_fails PASSED [ 26%]
test_crypto_vault.py::TestCryptoVault::test_tampered_tag_fails PASSED    [ 27%]
test_crypto_vault.py::TestCryptoVault::test_tampered_iv_fails PASSED     [ 28%]
test_crypto_vault.py::TestCryptoVault::test_empty_plaintext_fails PASSED [ 29%]
test_crypto_vault.py::TestCryptoVault::test_base64_encoding PASSED       [ 30%]
test_crypto_vault.py::TestCryptoVault::test_deterministic_key_derivation PASSED [ 30%]
test_crypto_vault.py::TestCryptoVault::test_unique_iv_per_encryption PASSED [ 31%]
test_observability.py::TestHealthChecks::test_health_endpoint_public ERROR [ 32%]
test_observability.py::TestHealthChecks::test_readiness_endpoint_public ERROR [ 33%]
test_observability.py::TestHealthChecks::test_health_has_no_sensitive_info ERROR [ 34%]
test_observability.py::TestMetricsEndpoint::test_metrics_requires_auth_or_localhost ERROR [ 34%]
test_observability.py::TestMetricsEndpoint::test_metrics_prometheus_format ERROR [ 35%]
test_observability.py::TestMetricsEndpoint::test_metrics_json_format ERROR [ 36%]
test_observability.py::TestRequestIdPropagation::test_request_id_generated_when_missing ERROR [ 37%]
test_observability.py::TestRequestIdPropagation::test_request_id_preserved_when_provided ERROR [ 38%]
test_observability.py::TestRequestIdPropagation::test_request_id_stable_across_endpoints ERROR [ 39%]
test_observability.py::TestTaskPolicy::test_task_policy_blocks_dangerous_commands ERROR [ 39%]
test_observability.py::TestTaskPolicy::test_task_policy_allows_safe_commands ERROR [ 40%]
test_observability.py::TestTaskPolicy::test_task_policy_allowlist_mode ERROR [ 41%]
test_observability.py::TestAuditLogExport::test_audit_export_csv_requires_admin ERROR [ 42%]
test_observability.py::TestAuditLogExport::test_audit_export_json_requires_admin ERROR [ 43%]
test_observability.py::TestAuditLogExport::test_audit_export_csv_with_admin ERROR [ 43%]
test_observability.py::TestAuditLogExport::test_audit_export_json_with_admin ERROR [ 44%]
test_plugin_integration.py::test_plugin_integration PASSED               [ 45%]
test_plugin_system.py::TestEventModel::test_create_event_helper PASSED   [ 46%]
test_plugin_system.py::TestEventModel::test_event_creation PASSED        [ 47%]
test_plugin_system.py::TestEventModel::test_event_from_audit_log PASSED  [ 47%]
test_plugin_system.py::TestEventModel::test_event_to_dict PASSED         [ 48%]
test_plugin_system.py::TestEventModel::test_event_to_json PASSED         [ 49%]
test_plugin_system.py::TestPluginInterface::test_plugin_creation PASSED  [ 50%]
test_plugin_system.py::TestPluginInterface::test_plugin_hooks_are_optional PASSED [ 51%]
test_plugin_system.py::TestPluginManager::test_allowlist_parsing PASSED  [ 52%]
test_plugin_system.py::TestPluginManager::test_disabled_plugin_not_called PASSED [ 52%]
test_plugin_system.py::TestPluginManager::test_empty_allowlist PASSED    [ 53%]
test_plugin_system.py::TestPluginManager::test_event_dispatch_when_disabled PASSED [ 54%]
test_plugin_system.py::TestPluginManager::test_event_routing PASSED      [ 55%]
test_plugin_system.py::TestPluginManager::test_plugin_error_isolation PASSED [ 56%]
test_plugin_system.py::TestPluginManager::test_plugin_system_disabled_by_default PASSED [ 56%]
test_plugin_system.py::TestPluginManager::test_plugin_system_enabled PASSED [ 57%]
test_plugin_system.py::TestPluginManager::test_shutdown_notification PASSED [ 58%]
test_plugin_system.py::TestPluginManager::test_startup_notification PASSED [ 59%]
test_plugin_system.py::TestEventTypes::test_event_types_defined PASSED   [ 60%]
test_plugin_system.py::TestEventTypes::test_severity_levels PASSED       [ 60%]
test_rate_limiter.py::TestRateLimiter::test_allow_within_limit PASSED    [ 61%]
test_rate_limiter.py::TestRateLimiter::test_block_when_exceeded PASSED   [ 62%]
test_rate_limiter.py::TestRateLimiter::test_cleanup_old_buckets PASSED   [ 63%]
test_rate_limiter.py::TestRateLimiter::test_clear_all PASSED             [ 64%]
test_rate_limiter.py::TestRateLimiter::test_different_keys_independent PASSED [ 65%]
test_rate_limiter.py::TestRateLimiter::test_rate_info_structure PASSED   [ 65%]
test_rate_limiter.py::TestRateLimiter::test_reset PASSED                 [ 66%]
test_rate_limiter.py::TestRateLimiter::test_token_bucket_refill PASSED   [ 67%]
test_rate_limiter.py::TestRateLimiterSingleton::test_get_rate_limiter_singleton PASSED [ 68%]
test_rate_limiter.py::TestEndpointRateLimits::test_check_endpoint_rate_limit_allowed PASSED [ 69%]
test_rate_limiter.py::TestEndpointRateLimits::test_check_endpoint_rate_limit_blocked PASSED [ 69%]
test_rate_limiter.py::TestEndpointRateLimits::test_check_endpoint_rate_limit_unknown_endpoint PASSED [ 70%]
test_rate_limiter.py::TestEndpointRateLimits::test_inventory_refresh_rate_limit PASSED [ 71%]
test_rate_limiter.py::TestEndpointRateLimits::test_task_create_rate_limit PASSED [ 72%]
test_rate_limiter.py::TestEndpointRateLimits::test_webhook_test_rate_limit PASSED [ 73%]
test_security.py::test_rate_limiting FAILED                              [ 73%]
test_security.py::test_login_rate_limiting FAILED                        [ 74%]
test_security.py::test_cors_headers FAILED                               [ 75%]
test_security.py::test_security_headers FAILED                           [ 76%]
test_security.py::test_input_validation_invalid_ip FAILED                [ 77%]
test_security.py::test_input_validation_invalid_port FAILED              [ 78%]
test_webhooks.py::TestWebhookDatabase::test_create_webhook PASSED        [ 78%]
test_webhooks.py::TestWebhookDatabase::test_delete_webhook PASSED        [ 79%]
test_webhooks.py::TestWebhookDatabase::test_get_webhook PASSED           [ 80%]
test_webhooks.py::TestWebhookDatabase::test_get_webhook_deliveries PASSED [ 81%]
test_webhooks.py::TestWebhookDatabase::test_get_webhook_not_found PASSED [ 82%]
test_webhooks.py::TestWebhookDatabase::test_get_webhooks PASSED          [ 82%]
test_webhooks.py::TestWebhookDatabase::test_log_webhook_delivery PASSED  [ 83%]
test_webhooks.py::TestWebhookDatabase::test_update_webhook PASSED        [ 84%]
test_webhooks.py::TestWebhookDatabase::test_update_webhook_clear_secret PASSED [ 85%]
test_webhooks.py::TestWebhookDatabase::test_update_webhook_last_triggered PASSED [ 86%]
test_webhooks.py::TestWebhookDatabase::test_webhook_event_types_json PASSED [ 86%]
test_webhooks.py::TestSSRFProtection::test_block_0_0_0_0 PASSED          [ 87%]
test_webhooks.py::TestSSRFProtection::test_block_127_0_0_1 PASSED        [ 88%]
test_webhooks.py::TestSSRFProtection::test_block_internal_domains PASSED [ 89%]
test_webhooks.py::TestSSRFProtection::test_block_invalid_scheme PASSED   [ 90%]
test_webhooks.py::TestSSRFProtection::test_block_ipv6_localhost PASSED   [ 91%]
test_webhooks.py::TestSSRFProtection::test_block_localhost PASSED        [ 91%]
test_webhooks.py::TestSSRFProtection::test_block_private_ip_10 PASSED    [ 92%]
test_webhooks.py::TestSSRFProtection::test_block_private_ip_172 PASSED   [ 93%]
test_webhooks.py::TestSSRFProtection::test_block_private_ip_192 PASSED   [ 94%]
test_webhooks.py::TestSSRFProtection::test_safe_http_url PASSED          [ 95%]
test_webhooks.py::TestSSRFProtection::test_safe_https_url PASSED         [ 95%]
test_webhooks.py::TestWebhookDispatcher::test_dispatch_hmac_signature PASSED [ 96%]
test_webhooks.py::TestWebhookDispatcher::test_dispatch_to_webhooks_success PASSED [ 97%]
test_webhooks.py::TestWebhookDispatcher::test_dispatch_with_event_type_filter PASSED [ 98%]
test_webhooks.py::TestWebhookDispatcher::test_retry_on_failure PASSED    [ 99%]
test_webhooks.py::TestWebhookDispatcher::test_ssrf_protection_blocks_delivery PASSED [100%]

==================================== ERRORS ====================================
___________ ERROR at setup of TestAuthentication.test_login_success ____________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_____ ERROR at setup of TestAuthentication.test_login_invalid_credentials ______
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
________ ERROR at setup of TestAuthentication.test_login_missing_fields ________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
____________ ERROR at setup of TestAuthentication.test_verify_token ____________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
________ ERROR at setup of TestAuthentication.test_verify_invalid_token ________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_____________ ERROR at setup of TestServerCRUD.test_create_server ______________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
______________ ERROR at setup of TestServerCRUD.test_list_servers ______________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
____________ ERROR at setup of TestServerCRUD.test_get_server_by_id ____________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_____________ ERROR at setup of TestServerCRUD.test_update_server ______________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_____________ ERROR at setup of TestServerCRUD.test_delete_server ______________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
___________ ERROR at setup of TestStatistics.test_get_overview_stats ___________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_____________ ERROR at setup of TestExport.test_export_servers_csv _____________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
____________ ERROR at setup of TestExport.test_export_servers_json _____________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
___________ ERROR at setup of TestEmailConfig.test_get_email_config ____________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
__________ ERROR at setup of TestEmailConfig.test_update_email_config __________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
______ ERROR at setup of TestUnauthorizedAccess.test_list_servers_no_auth ______
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_____ ERROR at setup of TestUnauthorizedAccess.test_create_server_no_auth ______
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_____ ERROR at setup of TestUnauthorizedAccess.test_delete_server_no_auth ______
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
________________________ ERROR at setup of test_summary ________________________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_api.py:28: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
________ ERROR at setup of TestHealthChecks.test_health_endpoint_public ________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
______ ERROR at setup of TestHealthChecks.test_readiness_endpoint_public _______
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_____ ERROR at setup of TestHealthChecks.test_health_has_no_sensitive_info _____
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_ ERROR at setup of TestMetricsEndpoint.test_metrics_requires_auth_or_localhost _
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_____ ERROR at setup of TestMetricsEndpoint.test_metrics_prometheus_format _____
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
________ ERROR at setup of TestMetricsEndpoint.test_metrics_json_format ________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_ ERROR at setup of TestRequestIdPropagation.test_request_id_generated_when_missing _
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_ ERROR at setup of TestRequestIdPropagation.test_request_id_preserved_when_provided _
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_ ERROR at setup of TestRequestIdPropagation.test_request_id_stable_across_endpoints _
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_ ERROR at setup of TestTaskPolicy.test_task_policy_blocks_dangerous_commands __
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
____ ERROR at setup of TestTaskPolicy.test_task_policy_allows_safe_commands ____
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_______ ERROR at setup of TestTaskPolicy.test_task_policy_allowlist_mode _______
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
__ ERROR at setup of TestAuditLogExport.test_audit_export_csv_requires_admin ___
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
__ ERROR at setup of TestAuditLogExport.test_audit_export_json_requires_admin __
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
____ ERROR at setup of TestAuditLogExport.test_audit_export_csv_with_admin _____
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
____ ERROR at setup of TestAuditLogExport.test_audit_export_json_with_admin ____
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_observability.py:26: in setup_auth
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
=================================== FAILURES ===================================
______________________________ test_rate_limiting ______________________________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/stats/overview (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_security.py:21: in test_rate_limiting
    response = requests.get(f"{BASE_URL}/api/stats/overview")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:73: in get
    return request("get", url, params=params, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/stats/overview (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
___________________________ test_login_rate_limiting ___________________________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_security.py:36: in test_login_rate_limiting
    response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
______________________________ test_cors_headers _______________________________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/stats/overview (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_security.py:53: in test_cors_headers
    response = requests.get(f"{BASE_URL}/api/stats/overview")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:73: in get
    return request("get", url, params=params, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/stats/overview (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
____________________________ test_security_headers _____________________________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/stats/overview (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_security.py:62: in test_security_headers
    response = requests.get(f"{BASE_URL}/api/stats/overview")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:73: in get
    return request("get", url, params=params, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/stats/overview (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
_______________________ test_input_validation_invalid_ip _______________________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_security.py:81: in test_input_validation_invalid_ip
    login_response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
______________________ test_input_validation_invalid_port ______________________
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:204: in _new_conn
    sock = connection.create_connection(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:85: in create_connection
    raise err
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:787: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:493: in _make_request
    conn.request(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:500: in request
    self.endheaders()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1298: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:1058: in _send_output
    self.send(msg)
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/http/client.py:996: in send
    self.connect()
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:644: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/connectionpool.py:841: in urlopen
    retries = retries.increment(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/urllib3/util/retry.py:535: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))

During handling of the above exception, another exception occurred:
test_security.py:107: in test_input_validation_invalid_port
    login_response = requests.post(
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:115: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/sessions.py:703: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/requests/adapters.py:677: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
=========================== short test summary info ============================
FAILED test_security.py::test_rate_limiting - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/stats/overview (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
FAILED test_security.py::test_login_rate_limiting - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
FAILED test_security.py::test_cors_headers - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/stats/overview (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
FAILED test_security.py::test_security_headers - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/stats/overview (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
FAILED test_security.py::test_input_validation_invalid_ip - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
FAILED test_security.py::test_input_validation_invalid_port - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestAuthentication::test_login_success - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestAuthentication::test_login_invalid_credentials - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestAuthentication::test_login_missing_fields - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestAuthentication::test_verify_token - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestAuthentication::test_verify_invalid_token - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestServerCRUD::test_create_server - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestServerCRUD::test_list_servers - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestServerCRUD::test_get_server_by_id - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestServerCRUD::test_update_server - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestServerCRUD::test_delete_server - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestStatistics::test_get_overview_stats - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestExport::test_export_servers_csv - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestExport::test_export_servers_json - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestEmailConfig::test_get_email_config - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestEmailConfig::test_update_email_config - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestUnauthorizedAccess::test_list_servers_no_auth - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestUnauthorizedAccess::test_create_server_no_auth - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::TestUnauthorizedAccess::test_delete_server_no_auth - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_api.py::test_summary - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestHealthChecks::test_health_endpoint_public - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestHealthChecks::test_readiness_endpoint_public - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestHealthChecks::test_health_has_no_sensitive_info - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestMetricsEndpoint::test_metrics_requires_auth_or_localhost - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestMetricsEndpoint::test_metrics_prometheus_format - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestMetricsEndpoint::test_metrics_json_format - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestRequestIdPropagation::test_request_id_generated_when_missing - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestRequestIdPropagation::test_request_id_preserved_when_provided - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestRequestIdPropagation::test_request_id_stable_across_endpoints - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestTaskPolicy::test_task_policy_blocks_dangerous_commands - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestTaskPolicy::test_task_policy_allows_safe_commands - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestTaskPolicy::test_task_policy_allowlist_mode - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestAuditLogExport::test_audit_export_csv_requires_admin - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestAuditLogExport::test_audit_export_json_requires_admin - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestAuditLogExport::test_audit_export_csv_with_admin - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
ERROR test_observability.py::TestAuditLogExport::test_audit_export_json_with_admin - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=9083): Max retries exceeded with url: /api/auth/login (Caused by NewConnectionError("HTTPConnection(host='localhost', port=9083): Failed to establish a new connection: [Errno 111] Connection refused"))
=================== 6 failed, 82 passed, 35 errors in 11.11s ===================
```

### 3. Build Validation

**Frontend Build:** ⚠️ UNKNOWN

### 4. Smoke Tests

**Result:** ⚠️ UNKNOWN

#### Smoke Test Details:
```
```

### 5. UI Screenshots

**Result:** ⚠️ SKIPPED

Screenshots are available in `docs/screenshots/` directory.

---

## Module Coverage

The following modules were checked during this review:

- ✅ **Authentication & RBAC:** `backend/user_management.py`, `backend/security.py`
- ✅ **Webhooks:** `backend/webhook_dispatcher.py`
- ✅ **Task Management:** `backend/task_runner.py`, `backend/task_policy.py`
- ✅ **Inventory:** `backend/inventory_collector.py`
- ✅ **Terminal:** `backend/terminal.py`, `backend/websocket_server.py`
- ✅ **Audit:** `backend/event_model.py`, `backend/audit_cleanup.py`
- ✅ **Plugins:** `backend/plugin_system.py`, `backend/plugins/`
- ✅ **Crypto Vault:** `backend/crypto_vault.py`, `backend/ssh_key_manager.py`
- ✅ **Rate Limiting:** `backend/rate_limiter.py`
- ✅ **Cache:** `backend/cache_helper.py`
- ✅ **Frontend:** `frontend-next/src/`

---

## Findings

### Documentation Consistency

#### Checked Documentation Files:

- ✅ `README.md` exists
- ✅ `DEPLOYMENT.md` exists
- ✅ `SECURITY.md` exists
- ✅ `ARCHITECTURE.md` exists
- ✅ `ROADMAP.md` exists
- ✅ `TODO-IMPROVEMENTS.md` exists

#### OpenAPI Specification

- ✅ `docs/openapi.yaml` exists

### Potential Issues

#### Code TODOs and FIXMEs:

Found **0
0** TODO/FIXME comments in code

#### Security Scan:

Run `bandit -r backend/` for detailed security analysis


### Missing Tests

Review test coverage to identify modules that need additional testing.

Run: `pytest --cov=backend --cov-report=html` for detailed coverage report

---

## Suggested Next PRs

Based on this review, consider the following improvements:

### High Priority

1. **Fix any failing tests** - Address test failures identified in this report
2. **Security fixes** - Address any security issues from bandit scan
3. **Documentation updates** - Fix broken links and update outdated sections

### Medium Priority

1. **Increase test coverage** - Add tests for modules with <80% coverage
2. **Code cleanup** - Address TODO/FIXME comments
3. **Performance optimization** - Profile slow endpoints and optimize

### Low Priority

1. **UI/UX improvements** - Based on screenshot review
2. **Documentation enhancements** - Add more examples and use cases
3. **Developer experience** - Improve setup and development workflow

---

## Copilot Agent Task Prompt

If you want to delegate follow-up tasks to GitHub Copilot agent, use this prompt:

```
Review the automated project review report at docs/REVIEW_REPORT.md and address the following:

1. Fix any failing tests identified in the test results
2. Address security issues found by bandit scan
3. Update documentation based on the findings
4. Add missing tests for modules with low coverage
5. Clean up TODO/FIXME comments in the codebase

Create focused PRs for each major issue found. Ensure all changes maintain backward compatibility and don't break existing functionality.
```

---

## Release Checklist

Before releasing the next version, ensure:

- [ ] All CI checks pass (lint, test, build, smoke)
- [ ] No critical security vulnerabilities
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated
- [ ] Version numbers are bumped appropriately
- [ ] Screenshots reflect current UI state
- [ ] All TODOs in ROADMAP.md are reviewed
- [ ] Deployment guide is tested and accurate

---

## Artifacts

The following artifacts were generated during this review:

- Test results: See GitHub Actions artifacts
- Lint results: See GitHub Actions artifacts
- Screenshots: `docs/screenshots/`
- Review report: `docs/REVIEW_REPORT.md` (this file)

---

**Report Generated By:** GitHub Actions Manual Project Review Workflow  
**Next Review:** Run workflow manually when significant changes are made
