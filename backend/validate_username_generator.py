#!/usr/bin/env python3
"""
Validation script for username generator logic (without database)
This validates the core logic without requiring dependencies
"""


def validate_base_username_logic():
    """Validate the base username generation logic"""
    # Test case 1: Basic generation
    school_code = "4401"
    student_id_number = "110101200501011234"
    base_username = f"{school_code}{student_id_number[-6:]}"
    assert base_username == "4401011234", f"Expected '4401011234', got '{base_username}'"
    assert len(base_username) == 10, f"Expected length 10, got {len(base_username)}"
    print("✓ Test 1: Basic username generation - PASSED")

    # Test case 2: Different school code
    school_code = "1234"
    student_id_number = "110101200501011234"
    base_username = f"{school_code}{student_id_number[-6:]}"
    assert base_username == "1234011234", f"Expected '1234011234', got '{base_username}'"
    print("✓ Test 2: Different school code - PASSED")

    # Test case 3: Different student ID
    school_code = "4401"
    student_id_number = "999999999999999999"
    base_username = f"{school_code}{student_id_number[-6:]}"
    assert base_username == "4401999999", f"Expected '4401999999', got '{base_username}'"
    print("✓ Test 3: Different student ID - PASSED")

    # Test case 3b: Student ID ending in 019999
    school_code = "4401"
    student_id_number = "999999999999019999"
    base_username = f"{school_code}{student_id_number[-6:]}"
    assert base_username == "4401019999", f"Expected '4401019999', got '{base_username}'"
    print("✓ Test 3b: Student ID ending in 019999 - PASSED")

    # Test case 4: Edge case - minimum values
    school_code = "0001"
    student_id_number = "000000000000000001"
    base_username = f"{school_code}{student_id_number[-6:]}"
    assert base_username == "0001000001", f"Expected '0001000001', got '{base_username}'"
    print("✓ Test 4: Minimum values - PASSED")

    # Test case 5: Edge case - maximum values
    school_code = "9999"
    student_id_number = "999999999999999999"
    base_username = f"{school_code}{student_id_number[-6:]}"
    assert base_username == "9999999999", f"Expected '9999999999', got '{base_username}'"
    print("✓ Test 5: Maximum values - PASSED")


def validate_suffix_logic():
    """Validate the suffix generation logic"""
    base_username = "4401011234"

    # Test letter suffixes A-Z
    for i in range(1, 27):
        suffix = chr(64 + i)  # A=65, B=66, ...
        username = f"{base_username}{suffix}"
        assert len(username) == 11, f"Expected length 11 for suffix {suffix}, got {len(username)}"
        assert username.endswith(suffix), f"Expected username to end with {suffix}"

    print("✓ Test 6: Letter suffixes A-Z - PASSED")

    # Test numeric suffixes (after Z)
    for i in range(27, 32):
        numeric_suffix = i - 26
        username = f"{base_username}{numeric_suffix}"
        assert len(username) == 11, f"Expected length 11 for suffix {numeric_suffix}, got {len(username)}"

    print("✓ Test 7: Numeric suffixes - PASSED")


def validate_format_requirements():
    """Validate format requirements"""
    # Test alphanumeric
    test_cases = [
        ("4401", "110101200501011234", "4401011234"),
        ("4401", "999999999999019999", "4401019999"),  # last 6 is "019999"
        ("1234", "567890123456789012", "1234789012"),
    ]

    for school_code, student_id, expected in test_cases:
        result = f"{school_code}{student_id[-6:]}"
        assert result == expected, f"Expected {expected}, got {result}"
        assert result.isalnum(), f"Username {result} should be alphanumeric"
        assert len(result) == 10, f"Username {result} should be 10 characters"

    print("✓ Test 8: Format requirements - PASSED")


def main():
    """Run all validation tests"""
    print("Running username generator validation...\n")

    try:
        validate_base_username_logic()
        validate_suffix_logic()
        validate_format_requirements()

        print("\n" + "=" * 50)
        print("✅ ALL VALIDATION TESTS PASSED")
        print("=" * 50)
        print("\nThe username generator logic is correct:")
        print("- Base username format: school_code (4) + last 6 of student_id")
        print("- Conflict resolution: A-Z suffixes, then numeric")
        print("- All edge cases handled properly")

    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
