HTTP status codes are grouped into 5 categories:

- **1xx** → Informational
- **2xx** → Success
- **3xx** → Redirection
- **4xx** → Client Errors
- **5xx** → Server Errors

---

# 1xx — Informational Responses

|Code|Name|Description|
|---|---|---|
|100|Continue|Request headers received, continue sending body|
|101|Switching Protocols|Server switches protocol (e.g., HTTP → WebSocket)|
|102|Processing|Server is processing request|
|103|Early Hints|Sends preliminary headers before final response|

---

# 2xx — Success Responses

|Code|Name|Description|
|---|---|---|
|200|OK|Request succeeded|
|201|Created|Resource successfully created|
|202|Accepted|Request accepted but not completed yet|
|203|Non-Authoritative Information|Response modified by proxy|
|204|No Content|Success with no response body|
|205|Reset Content|Client should reset document/view|
|206|Partial Content|Partial response returned (range requests)|
|207|Multi-Status|Multiple status values returned|
|208|Already Reported|DAV binding already reported|
|226|IM Used|Instance manipulation applied|

---

# 3xx — Redirection Responses

|Code|Name|Description|
|---|---|---|
|300|Multiple Choices|Multiple possible responses|
|301|Moved Permanently|Resource permanently moved|
|302|Found|Temporary redirect|
|303|See Other|Redirect using GET|
|304|Not Modified|Cached version still valid|
|305|Use Proxy|Must access through proxy (deprecated)|
|306|Switch Proxy|Unused/deprecated|
|307|Temporary Redirect|Temporary redirect preserving method|
|308|Permanent Redirect|Permanent redirect preserving method|

---

# 4xx — Client Error Responses

|Code|Name|Description|
|---|---|---|
|400|Bad Request|Invalid request syntax|
|401|Unauthorized|Authentication required|
|402|Payment Required|Reserved for future use|
|403|Forbidden|Access denied|
|404|Not Found|Resource not found|
|405|Method Not Allowed|HTTP method not supported|
|406|Not Acceptable|Cannot generate acceptable response|
|407|Proxy Authentication Required|Proxy authentication needed|
|408|Request Timeout|Client took too long|
|409|Conflict|Request conflicts with server state|
|410|Gone|Resource permanently removed|
|411|Length Required|`Content-Length` missing|
|412|Precondition Failed|Preconditions in headers failed|
|413|Payload Too Large|Request body too large|
|414|URI Too Long|URL too long|
|415|Unsupported Media Type|Unsupported content type|
|416|Range Not Satisfiable|Invalid range request|
|417|Expectation Failed|`Expect` header unmet|
|418|I'm a teapot|Joke status from RFC 2324|
|421|Misdirected Request|Request sent to wrong server|
|422|Unprocessable Entity|Validation failed|
|423|Locked|Resource is locked|
|424|Failed Dependency|Dependent request failed|
|425|Too Early|Server unwilling to process early request|
|426|Upgrade Required|Must switch protocols|
|428|Precondition Required|Conditional request required|
|429|Too Many Requests|Rate limit exceeded|
|431|Request Header Fields Too Large|Headers too large|
|451|Unavailable For Legal Reasons|Blocked for legal reasons|

---

# 5xx — Server Error Responses

|Code|Name|Description|
|---|---|---|
|500|Internal Server Error|Generic server failure|
|501|Not Implemented|Functionality not supported|
|502|Bad Gateway|Invalid upstream response|
|503|Service Unavailable|Server temporarily unavailable|
|504|Gateway Timeout|Upstream server timeout|
|505|HTTP Version Not Supported|HTTP version unsupported|
|506|Variant Also Negotiates|Configuration error|
|507|Insufficient Storage|Server lacks storage|
|508|Loop Detected|Infinite loop detected|
|510|Not Extended|Further extensions required|
|511|Network Authentication Required|Network login required|

---

# Most Commonly Used HTTP Codes

|Code|Meaning|Typical Scenario|
|---|---|---|
|200|OK|Successful API call|
|201|Created|User/resource created|
|204|No Content|Delete success|
|301|Moved Permanently|SEO redirect|
|302|Found|Temporary redirect|
|304|Not Modified|Browser cache hit|
|400|Bad Request|Invalid JSON/input|
|401|Unauthorized|Missing token/login|
|403|Forbidden|No permission|
|404|Not Found|API endpoint missing|
|409|Conflict|Duplicate resource|
|422|Unprocessable Entity|Validation error|
|429|Too Many Requests|Rate limit exceeded|
|500|Internal Server Error|Backend crash|
|502|Bad Gateway|Reverse proxy issue|
|503|Service Unavailable|Maintenance/overload|
|504|Gateway Timeout|Upstream service slow|

---

# Easy Way to Remember

```
1xx → Hold on
2xx → Success
3xx → Go somewhere else
4xx → You did something wrong
5xx → Server did something wrong
```

---

# Example HTTP Response

```
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": "User not found"
}
```

---

# REST API Best Practices

|Scenario|Recommended Code|
|---|---|
|Login required|401|
|Access denied|403|
|Validation failed|422|
|Resource missing|404|
|Resource created|201|
|Delete success|204|
|Duplicate resource|409|
|Rate limiting|429|
|Unexpected backend failure|500|