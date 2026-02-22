
import re

def test_regex():
    # AWS Access Key
    pattern_ak = r'AKIA[0-9A-Z]{12,20}'
    text_ak = "aws_access_key_id = AKIAIOSFODNN7EXAMPLE"
    match_ak = re.search(pattern_ak, text_ak, re.IGNORECASE)
    print(f"Access Key Match: {match_ak}")
    if match_ak:
        print(f"Matched text: {match_ak.group(0)}")

    # AWS Secret Key
    pattern_sk = r'aws_secret_access_key\s*=\s*["\']([A-Za-z0-9/+=]{35,45})["\']'
    text_sk = "aws_secret_access_key = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'"
    match_sk = re.search(pattern_sk, text_sk, re.IGNORECASE)
    print(f"Secret Key Match: {match_sk}")
    if match_sk:
        print(f"Matched text: {match_sk.group(0)}")
        print(f"Group 1: {match_sk.group(1)}")

if __name__ == "__main__":
    test_regex()
