# Troubleshooting: Customer Login Issues

This guide provides steps for customer support representatives to assist users experiencing difficulties logging into the dBank Web or Mobile applications.

## Common Scenarios and Solutions

### 1. "Invalid Username or Password" Error
- **Verify Credentials:** Ask the customer to ensure there are no trailing spaces and that Caps Lock is disabled.
- **Password Reset:** If they forgot their password, guide them to click the "Forgot Password" link on the login screen. They will need access to their registered email address.
- **Account Lockout:** After 5 consecutive failed login attempts, the account is temporarily locked for 30 minutes for security reasons. Representatives can manually unlock the account via the Admin Portal after verifying the customer's identity (requires PIN and Date of Birth).

### 2. Not Receiving 2FA SMS Code
- **Signal/Network Issues:** Ask the user to verify their phone has cellular reception and is not in Airplane mode.
- **Delayed Delivery:** Sometimes SMS gateways experience delays. Advise the user to wait up to 2 minutes before requesting a new code.
- **Alternative Method:** If the user has an Authenticator App configured (available since v1.2), suggest they use that instead of SMS.
- **Change of Phone Number:** If the user lost access to their registered phone number, they must call the verified support line. A manual identity verification process involving government ID is required to update the phone number.

### 3. "Session Expired" Loop
- This often happens due to stale browser cookies.
- **Clear Cache/Cookies:** Instruct the user to clear their browser's cache and cookies for `*.dbank.com`.
- **Try Incognito Mode:** Ask the user to try logging in using an Incognito/Private browsing window to isolate extension or cookie issues.
- **Check Device Time:** Ensure the device's date, time, and timezone settings are set to "Automatic." Incorrect system time can invalidate authentication tokens.