# AtmoGraph - Detailed Test Cases

## 1. Introduction

This document describes test cases designed to validate the AtmoGraph Supply Chain Ripple Effect Predictor. The tests cover API functionality, database connectivity, graph operations, company search, and input validation.

## 2. Detailed Test Cases

| Test ID | Component | Test Scenario | Input | Expected Result |
|---|---|---|---|---|
| TC01 | Health API | Check backend availability | GET health endpoint | Successful response indicating backend status |
| TC02 | Database | Check database connectivity | Database connection request | Database connection status is returned |
| TC03 | Graph API | Retrieve graph statistics | Valid graph request | Node and relationship counts are returned |
| TC04 | Graph API | Retrieve graph data | Valid graph request | Graph nodes and relationships are returned |
| TC05 | Search API | Search for an existing company | Valid company name | Matching company details are returned |
| TC06 | Search API | Search for an unknown company | Non-existing company name | Empty result is handled correctly |
| TC07 | Node API | Retrieve an existing node | Valid node ID | Node details are returned |
| TC08 | Node API | Retrieve an invalid node | Invalid node ID | Appropriate error response is returned |
| TC09 | Prediction API | Request disruption prediction | Valid prediction parameters | Prediction result is returned |
| TC10 | Prediction API | Submit invalid prediction parameters | Missing or invalid parameters | Validation error is returned |

## 3. Positive Test Cases

Positive testing verifies application behaviour with valid inputs.

- TC01: Verify that the backend health endpoint responds successfully.
- TC02: Verify that the application can connect to the database.
- TC03: Verify that graph statistics are retrieved correctly.
- TC04: Verify that graph data contains valid nodes and relationships.
- TC05: Verify that searching for an existing company returns matching results.
- TC07: Verify that valid node identifiers return node details.
- TC09: Verify that valid prediction parameters produce a prediction response.

## 4. Negative Test Cases

Negative testing verifies how the application handles invalid inputs and unexpected conditions.

- TC06: Verify that searching for an unknown company is handled correctly.
- TC08: Verify that an invalid node identifier produces an appropriate response.
- TC10: Verify that missing or invalid prediction parameters are rejected appropriately.

## 5. Validation Criteria

Each test case should be evaluated using the following criteria:

- Correctness of response data.
- Appropriate HTTP status codes.
- Proper error handling and messages.
- Handling of missing or invalid input.
- Consistency of graph and database information.

## 6. Test Execution Record

| Test ID | Actual Result | Status | Remarks |
|---|---|---|---|
| TC01-TC10 | Pending execution | Not Run | To be updated after testing the implemented application |

## 7. Conclusion

These test cases provide a structured approach to validating the functionality and reliability of AtmoGraph. Actual responses and pass/fail results must be recorded after executing the tests against the implemented application.