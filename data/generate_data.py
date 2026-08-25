"""
Generates a sample knowledge_base.csv with the same schema the notebook
expects: document_id, category, title, content, keywords.

Your real dataset (e.g. knowledge_base_improved.csv) was not included with
the notebook, so this script builds a realistic templated dataset instead,
so the whole app works out of the box. Replace data/knowledge_base.csv with
your real export at any time and re-run the backend (or call POST
/api/retrain) to pick it up.
"""
import csv
import itertools
import random
from pathlib import Path

random.seed(42)

OUTPUT_PATH = Path(__file__).parent / "knowledge_base.csv"

PLATFORMS = ["the Website", "the Mobile App", "Android", "iOS", "Desktop"]

# category -> list of (topic_title, action, content_template, keyword_list)
TOPICS = {
    "Authentication": [
        ("Login Password", "Reset",
         "If you can no longer use your sign-in password, you can restore access yourself in a few steps. "
         "Go to the sign-in page on {platform} and select the option to reset your password. Enter the email "
         "address linked to your account so a recovery message can be sent. Choose a new password you have not "
         "used before, mixing letters, numbers, and symbols. If these steps do not resolve it, contact support "
         "with your account email and any error message so we can look into it.",
         ["password recovery", "reset password", "identity verification", "regain access", "authentication"]),
        ("Two-Factor Authentication", "Enable",
         "You can set up two-step verification on {platform} in your security settings. Turning this on adds an "
         "extra layer of protection so a code is required in addition to your password. Choose to receive the "
         "code by text message, email, or an authenticator app. Keep a backup code stored somewhere safe in case "
         "you lose access to your device.",
         ["set up two-factor authentication", "enable two-factor authentication", "security code", "2fa", "otp"]),
        ("Login Errors", "Troubleshoot",
         "Problems signing in on {platform} are often caused by an outdated app version, an expired session, or "
         "a typo in your credentials. Clear your cache, confirm your internet connection, and make sure caps lock "
         "is off. If the issue continues after several attempts, your account may be temporarily locked for "
         "security reasons; wait a few minutes before trying again.",
         ["login not working", "login error", "technical issue", "sign in problem", "cannot log in"]),
        ("Verification Code", "Fix",
         "Most issues with a login code on {platform} clear up after requesting a fresh one, since codes expire "
         "quickly. Check that your phone number or email on file is current, and look in your spam folder for "
         "email codes. If codes never arrive, confirm your carrier is not blocking short codes.",
         ["verification code not working", "verification code delayed", "otp not received", "code expired"]),
        ("Authenticator App", "Set Up",
         "Setting up an authenticator app on {platform} takes only a minute and improves your account security. "
         "Download a supported authenticator app, scan the QR code shown in your security settings, and enter "
         "the six digit code it generates to confirm the link.",
         ["set up authenticator app", "enable authenticator app", "google authenticator", "totp setup"]),
        ("Biometric Login", "Enable",
         "Fingerprint and face unlock can be enabled on {platform} from the security section of your settings. "
         "This lets you sign in without typing your password each time, while still keeping your account "
         "protected on the device.",
         ["enable biometric login", "fingerprint login", "face id login", "device unlock"]),
        ("Account Lockout", "Resolve",
         "Repeated failed sign-in attempts on {platform} can temporarily lock your account as a security measure. "
         "Wait for the cooldown period to pass, or use the account recovery flow to verify your identity and "
         "regain access sooner.",
         ["account locked", "too many attempts", "unlock account", "temporary lockout"]),
        ("Session Expiration", "Understand",
         "For your security, {platform} automatically signs you out after a period of inactivity. Enable the "
         "remember me option on trusted personal devices to stay signed in longer between visits.",
         ["session expired", "signed out automatically", "stay logged in", "remember me option"]),
    ],
    "Billing and Payments": [
        ("Invoice", "Access",
         "You can view and download your invoices from {platform} at any time under the billing section of your "
         "account. Each invoice lists the charge date, amount, and payment method used, and can be exported as a "
         "PDF for your records.",
         ["download invoice", "view billing history", "receipt", "invoice pdf"]),
        ("Payment Method", "Update",
         "Updating your payment method on {platform} only takes a moment. Open your billing settings, remove the "
         "expired card, and add a new card or payment option. Future charges will automatically use the updated "
         "method.",
         ["update payment method", "change credit card", "add payment option", "expired card"]),
        ("Failed Payment", "Resolve",
         "A failed payment on {platform} is usually caused by insufficient funds, an expired card, or a bank "
         "decline. Update your payment details and retry the charge from your billing page to avoid any service "
         "interruption.",
         ["payment failed", "card declined", "billing issue", "retry payment"]),
        ("Refund", "Check Status",
         "You can check your refund status on {platform} in the billing history section. Refunds are typically "
         "processed within five to ten business days, though your bank may take longer to reflect the credit.",
         ["refund status", "refund process", "money back", "pending refund"]),
        ("Subscription Charge", "Understand",
         "Subscription charges on {platform} appear on the billing date shown in your account settings. If a "
         "charge looks unfamiliar, review your active plans and linked family or team members before contacting "
         "support.",
         ["unexpected charge", "subscription billing", "recurring payment", "billing cycle"]),
        ("Tax Invoice", "Request",
         "A formal tax invoice can be requested from {platform} through the billing help center. Provide your "
         "billing details and the invoice will be generated and emailed to you.",
         ["tax invoice", "vat invoice", "billing receipt request"]),
        ("Currency", "Change",
         "You can change your billing currency on {platform} from your account preferences. Note that pricing may "
         "vary slightly by region due to exchange rates and local taxes.",
         ["change currency", "billing currency", "pricing region"]),
        ("Payment History", "Review",
         "Your full payment history is available on {platform} under account activity. You can filter by date "
         "range and export the list for expense tracking.",
         ["payment history", "transaction history", "billing records"]),
    ],
    "Account Management": [
        ("Profile Details", "Update",
         "Updating your profile details on {platform} takes only a minute and helps keep your account information "
         "current. Open your account settings, edit your name, phone number, or address, and save the changes.",
         ["update profile", "edit account details", "change personal information"]),
        ("Email Address", "Change",
         "You can change the email address linked to your account on {platform} from the account settings page. "
         "A confirmation link will be sent to the new address, and it must be verified before the change takes "
         "effect.",
         ["change email", "update email address", "verify new email"]),
        ("Account Deletion", "Request",
         "If you want to permanently delete your account on {platform}, go to account settings and select the "
         "delete account option. This action removes your data and cannot be undone, so make sure to export "
         "anything you want to keep first.",
         ["delete account", "close account", "permanent account removal"]),
        ("Account Deactivation", "Request",
         "Deactivating your account on {platform} temporarily hides your profile without deleting your data. You "
         "can reactivate at any time simply by signing back in.",
         ["deactivate account", "temporary account pause", "hide profile"]),
        ("Duplicate Accounts", "Merge",
         "If you accidentally created more than one account on {platform}, contact support with both account "
         "emails to request a merge. This combines your history and settings into a single account.",
         ["merge accounts", "duplicate account", "combine accounts"]),
        ("Username", "Change",
         "Your username can be changed once every thirty days on {platform} from the profile settings page. "
         "Choose something unique, as usernames cannot be reused once released.",
         ["change username", "update display name"]),
        ("Profile Picture", "Update",
         "Updating your profile picture on {platform} is simple: open your profile, select the current image, and "
         "upload a new photo from your device.",
         ["update profile picture", "change avatar", "upload photo"]),
        ("Account Recovery", "Use",
         "If you lose access to your account on {platform}, the account recovery flow will ask you to verify your "
         "identity using a backup email, phone number, or security questions.",
         ["account recovery", "recover lost account", "identity verification"]),
    ],
    "Technical Support": [
        ("App Crashing", "Fix",
         "If {platform} keeps crashing, start by updating to the latest version, then restart your device. "
         "Clearing the app cache or reinstalling it often resolves crashes caused by corrupted temporary files.",
         ["app crashing", "app keeps closing", "force close", "app not responding"]),
        ("Slow Performance", "Improve",
         "Slow performance on {platform} can usually be improved by closing background apps, checking your "
         "internet connection speed, and clearing cached data from the settings menu.",
         ["app running slow", "performance issue", "lag", "loading slowly"]),
        ("Sync Issues", "Resolve",
         "If your data is not syncing on {platform}, confirm you are signed into the same account on all devices "
         "and that background sync is enabled in your settings.",
         ["sync not working", "data not syncing", "sync error"]),
        ("Notifications", "Fix",
         "If notifications are not appearing on {platform}, check that notification permissions are enabled at "
         "the device level and that do not disturb mode is turned off.",
         ["notifications not working", "push notifications disabled", "missing alerts"]),
        ("App Update", "Install",
         "Updating {platform} to the newest version brings bug fixes and performance improvements. Enable "
         "automatic updates in your app store settings so you never miss one.",
         ["update app", "latest version", "app update available"]),
        ("Bug Report", "Submit",
         "If you find a bug on {platform}, use the report a problem option in settings and include steps to "
         "reproduce it. Screenshots help our team resolve issues faster.",
         ["report a bug", "submit feedback", "app issue report"]),
        ("Error Codes", "Understand",
         "Error codes shown on {platform} usually include a short reference number. Search the help center for "
         "that code, or contact support with a screenshot for a faster diagnosis.",
         ["error code meaning", "what does this error mean", "troubleshoot error"]),
        ("Connectivity", "Fix",
         "Connectivity issues on {platform} are often resolved by switching between wifi and mobile data, "
         "restarting your router, or checking for a wider service outage.",
         ["connection issue", "cannot connect", "network error"]),
    ],
    "Privacy and Security": [
        ("Privacy Policy", "View",
         "You can view the privacy policy for {platform} at any time from the legal section of your settings. "
         "It explains what data is collected and how it is used.",
         ["check privacy policy", "privacy policy status", "data usage policy"]),
        ("Data Export", "Request",
         "You can request an export of your personal data on {platform} from the privacy settings page. The "
         "export is prepared as a downloadable file and usually ready within a few days.",
         ["export my data", "download personal data", "data portability"]),
        ("Data Deletion", "Request",
         "Requesting deletion of your personal data on {platform} can be done from the privacy settings. Some "
         "information may be retained briefly where required by law.",
         ["delete my data", "data removal request", "right to be forgotten"]),
        ("Device Management", "Review",
         "The device management page on {platform} lists every device currently signed into your account. Remove "
         "any device you do not recognize to keep your account secure.",
         ["manage devices", "signed in devices", "remove device access"]),
        ("Login Activity", "Review",
         "Reviewing your recent login activity on {platform} helps you spot anything you do not recognize. Look "
         "for unfamiliar locations or timestamps and change your password if something looks off.",
         ["review login activity", "recent sign ins", "suspicious activity"]),
        ("Permissions", "Manage",
         "App permissions on {platform} control what data and device features are shared. Review and adjust "
         "camera, location, and contact permissions at any time in settings.",
         ["manage permissions", "app permissions", "location access"]),
        ("Terms of Service", "Read",
         "The current terms of service for {platform} are available in the legal section of your account and "
         "outline the rules for using the product.",
         ["terms of service", "user agreement", "legal terms"]),
        ("Two-Step Verification", "Manage",
         "Two-step verification settings on {platform} can be reviewed, updated, or disabled from your security "
         "page at any time.",
         ["manage two step verification", "security settings review"]),
    ],
    "Orders and Shipping": [
        ("Order Tracking", "Check",
         "You can track your order on {platform} from the order history page. Tracking updates as the package "
         "moves through each shipping stage.",
         ["track order", "order status", "shipment tracking"]),
        ("Order Cancellation", "Request",
         "Orders can be canceled on {platform} within a short window after purchase, as long as the item has not "
         "already shipped. Go to order history and select cancel order.",
         ["cancel order", "stop shipment", "order cancellation window"]),
        ("Shipping Address", "Change",
         "You can update your shipping address on {platform} before an order ships. Once a package is in transit, "
         "contact support to see if a redirection is possible.",
         ["change shipping address", "update delivery address", "wrong address"]),
        ("Delayed Shipment", "Check",
         "If your shipment on {platform} is running later than expected, check the tracking page for the latest "
         "carrier update before reaching out, since most delays resolve within a few days.",
         ["delayed shipment", "late delivery", "package delayed"]),
        ("Returns", "Start",
         "Starting a return on {platform} is simple from the order history page. Print the prepaid label, pack "
         "the item securely, and drop it off at any listed carrier location.",
         ["return item", "start a return", "return label"]),
        ("Order Confirmation", "Find",
         "Your order confirmation on {platform} is emailed immediately after purchase and also available in your "
         "order history for reference.",
         ["order confirmation", "purchase receipt", "confirmation email missing"]),
        ("Out of Stock", "Check",
         "If an item is out of stock on {platform}, you can turn on restock notifications to be emailed as soon "
         "as it becomes available again.",
         ["out of stock", "restock notification", "item unavailable"]),
        ("Shipping Cost", "Understand",
         "Shipping costs on {platform} are calculated at checkout based on your location, order weight, and "
         "chosen delivery speed.",
         ["shipping cost", "delivery fee", "free shipping threshold"]),
    ],
    "Subscription and Plans": [
        ("Plan Upgrade", "Do",
         "Upgrading your plan on {platform} takes effect immediately and unlocks additional features right away. "
         "Any price difference is prorated for the current billing period.",
         ["upgrade plan", "unlock more features", "prorated charge"]),
        ("Plan Downgrade", "Do",
         "Downgrading your plan on {platform} takes effect at the start of your next billing cycle, so you keep "
         "your current features until then.",
         ["downgrade plan", "reduce plan tier"]),
        ("Subscription Cancellation", "Request",
         "You can cancel your subscription on {platform} at any time from the billing settings page. Access "
         "continues until the end of the current billing period.",
         ["cancel subscription", "stop recurring billing", "end plan"]),
        ("Free Trial", "Start",
         "Starting a free trial on {platform} gives you full access to premium features for a limited time, with "
         "no charge until the trial ends.",
         ["start free trial", "trial period", "free trial ending"]),
        ("Plan Comparison", "Review",
         "You can compare plans on {platform} side by side on the pricing page to see which features are included "
         "at each tier.",
         ["compare plans", "pricing details", "feature comparison"]),
        ("Auto-Renewal", "Manage",
         "Auto-renewal for your subscription on {platform} can be turned off from the billing settings if you do "
         "not want to be charged automatically at the end of your term.",
         ["turn off auto renewal", "manage renewal", "avoid automatic charge"]),
        ("Student Discount", "Apply",
         "A student discount can be applied on {platform} by verifying your student status through the "
         "verification partner linked in your billing settings.",
         ["student discount", "education pricing", "verify student status"]),
        ("Family Plan", "Set Up",
         "Setting up a family plan on {platform} lets you add multiple members under a single subscription and "
         "shared billing.",
         ["family plan", "shared subscription", "add family member"]),
    ],
    "General FAQ": [
        ("Getting Started", "Learn",
         "Getting started with {platform} takes only a minute. Create your account, complete your profile, and "
         "explore the quick tour to learn the basics.",
         ["getting started", "new user guide", "quick start"]),
        ("Pricing", "Check",
         "You can check current pricing for {platform} at any time on the pricing page, which lists every plan "
         "and its included features.",
         ["check pricing", "pricing details", "plan cost"]),
        ("Feature Overview", "Explore",
         "A full feature overview for {platform} is available in the help center, covering everything from basic "
         "setup to advanced tools.",
         ["feature overview", "what can it do", "product features"]),
        ("Contacting Support", "Learn",
         "You can contact support for {platform} through live chat, email, or the help center contact form for "
         "faster help with account specific issues.",
         ["contact support", "customer service", "get help"]),
        ("Accessibility", "Check",
         "Accessibility options for {platform} include screen reader support, adjustable text size, and high "
         "contrast display modes.",
         ["accessibility options", "screen reader support", "text size"]),
        ("Language Settings", "Change",
         "You can change the display language for {platform} from your account preferences at any time.",
         ["change language", "language settings", "localization"]),
        ("Common Questions", "Track",
         "This article explains what your most common question about {platform} usually covers and links to "
         "detailed guides for each topic.",
         ["common question", "faq", "help topics"]),
        ("Referral Program", "Join",
         "Joining the referral program on {platform} lets you earn rewards for inviting friends who sign up and "
         "become active users.",
         ["referral program", "invite friends", "earn rewards"]),
    ],
}

ACTION_TITLE_FORMATS = [
    "How to {action} Your {topic} on {platform}",
    "{action} Your {topic}: A Simple Guide",
    "{topic} {action_ing}: Step by Step",
    "Everything You Need to Know About {topic} on {platform}",
]


def build_rows():
    rows = []
    doc_num = 1
    for category, topics in TOPICS.items():
        for topic, action, content_template, keywords in topics:
            for platform in PLATFORMS:
                title_format = random.choice(ACTION_TITLE_FORMATS)
                title = title_format.format(
                    action=action,
                    action_ing=action.rstrip("e") + "ing" if action.endswith("e") else action + "ing",
                    topic=topic,
                    platform=platform,
                )
                content = content_template.format(platform=platform)
                keyword_str = ", ".join(keywords)
                rows.append({
                    "document_id": f"KB{doc_num:06d}",
                    "category": category,
                    "title": title,
                    "content": content,
                    "keywords": keyword_str,
                })
                doc_num += 1
    random.shuffle(rows)
    for i, row in enumerate(rows, start=1):
        row["document_id"] = f"KB{i:06d}"
    return rows


def main():
    rows = build_rows()
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["document_id", "category", "title", "content", "keywords"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
