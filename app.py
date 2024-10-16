from flask import Flask, request, jsonify
import dns.resolver
from ipwhois import IPWhois
import re
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

app = Flask(__name__)

# Set up rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the function to process domain data (the same code as before)
def get_ns_records(domain):
    try:
        result = dns.resolver.resolve(domain, 'NS')
        ns_records = [ns.to_text() for ns in result]
        return ns_records
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException) as e:
        logging.error(f"Error resolving NS records for {domain}: {e}")
        return None

def get_ip_from_ns(ns_record):
    try:
        result = dns.resolver.resolve(ns_record, 'A')
        ip_addresses = [ip.to_text() for ip in result]
        return ip_addresses
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException) as e:
        logging.error(f"Error resolving A records for NS {ns_record}: {e}")
        return None

def get_a_record(domain):
    try:
        result = dns.resolver.resolve(domain, 'A')
        ip_addresses = [ip.to_text() for ip in result]
        return ip_addresses
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException) as e:
        logging.error(f"Error resolving A records for {domain}: {e}")
        return None

def get_abuse_contact(rdap_result):
    abuse_contacts = []
    if isinstance(rdap_result, dict) and 'objects' in rdap_result:
        for entity_handle in rdap_result.get('entities', []):
            entity_data = rdap_result['objects'].get(entity_handle)
            if entity_data and 'roles' in entity_data:
                roles = entity_data.get('roles', [])
                if 'abuse' in roles:
                    contact_info = entity_data.get('contact', {})
                    emails = contact_info.get('email', [])
                    if isinstance(emails, list):
                        for email in emails:
                            if 'value' in email:
                                abuse_contacts.append(email['value'])
    return abuse_contacts

def get_hosting_info(ip_address):
    try:
        obj = IPWhois(ip_address)
        rdap_result = obj.lookup_rdap(depth=1)
        if isinstance(rdap_result, dict):
            hosting_provider = rdap_result.get('network', {}).get('name', None)
            abuse_contacts = get_abuse_contact(rdap_result)
            return hosting_provider, abuse_contacts
        return None, None
    except Exception as e:
        logging.error(f"Error getting hosting info for IP {ip_address}: {e}")
        return None, None

def get_unique_providers_and_abuse_contacts(hosting_providers, abuse_contacts):
    unique_providers = list(set(hosting_providers))
    unique_abuse_contacts = list(set(abuse_contacts))
    return unique_providers, unique_abuse_contacts

def get_ns_and_a_details(domain):
    hosting_providers = {"A": [], "NS": []}
    abuse_contacts = {"A": [], "NS": []}

    ns_records = get_ns_records(domain)
    if ns_records:
        for ns in ns_records:
            ip_addresses = get_ip_from_ns(ns.strip('.'))
            if ip_addresses:
                for ip_address in ip_addresses:
                    hosting_provider, abuse_contact = get_hosting_info(ip_address)
                    if hosting_provider:
                        hosting_providers["NS"].append(hosting_provider)
                    if abuse_contact:
                        abuse_contacts["NS"].extend(abuse_contact)

    a_records = get_a_record(domain)
    if a_records:
        for ip in a_records:
            hosting_provider, abuse_contact = get_hosting_info(ip)
            if hosting_provider:
                hosting_providers["A"].append(hosting_provider)
            if abuse_contact:
                abuse_contacts["A"].extend(abuse_contact)

    hosting_providers["A"], abuse_contacts["A"] = get_unique_providers_and_abuse_contacts(hosting_providers["A"], abuse_contacts["A"])
    hosting_providers["NS"], abuse_contacts["NS"] = get_unique_providers_and_abuse_contacts(hosting_providers["NS"], abuse_contacts["NS"])

    return {
        "HostingProviders": hosting_providers,
        "AbuseContacts": abuse_contacts
    }

# Validate domain name
def is_valid_domain(domain):
    regex = re.compile(
        r'^(?:[a-zA-Z0-9]' # First character of the domain
        r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)' # Sub domain + hostname
        r'+[a-zA-Z]{2,6}$' # First level TLD
    )
    return re.match(regex, domain) is not None

# Define the API endpoint
@app.route('/get-domain-details', methods=['POST'])
@limiter.limit("10 per minute")
def get_domain_details():
    # Get the domain from the POST request data
    data = request.get_json()
    domain = data.get('domain')

    if not domain:
        return jsonify({"error": "No domain provided"}), 400

    if not is_valid_domain(domain):
        return jsonify({"error": "Invalid domain provided"}), 400

    # Get the details for the domain
    result = get_ns_and_a_details(domain)

    # Return the result as JSON
    return jsonify(result)

# Set security headers
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=False)