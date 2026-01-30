## 0.3.1
- Fix bug where "Invalid user" failed login events were not parsed correctly if it did not include port number.
  - There is a difference in parsing "Invalid user root from 0.0.0.0 port 0" and "Invalid user root from 0.0.0.0"

## 0.3.0
- Map `LogonMethod` for successful and failed login events