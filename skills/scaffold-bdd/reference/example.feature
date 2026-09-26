@needs-postgres
Feature: Register users
  Users register through the public API and can be fetched back.

  Scenario: Register a new user over REST
    When I register "user@example.com" over REST
    Then the response status is 201
    And fetching the user over REST returns email "user@example.com"

  Scenario: Registering the same email twice is rejected
    Given "taken@example.com" is already registered over REST
    When I register "taken@example.com" over REST
    Then the response status is 409

  Scenario: Register a new user over gRPC
    When I register "grpc@example.com" over gRPC
    Then the gRPC call succeeds with email "grpc@example.com"
