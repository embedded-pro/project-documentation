Feature: FOC current control

  # REQ-FOC-001
  Scenario: Independent Id and Iq control
    Given a PMSM motor model running at steady state
    When a d-axis current reference of 0 A is applied
    And a q-axis current reference of 5 A is applied
    Then the d-axis current converges to 0 A within 10 ms
    And the q-axis current converges to 5 A within 10 ms

  # REQ-FOC-002
  Scenario: Clarke transform produces correct alpha-beta values
    Given three-phase currents ia = 1.0 A, ib = -0.5 A, ic = -0.5 A
    When the Clarke transform is applied
    Then alpha = 1.0 A
    And beta = 0.0 A

  # REQ-FOC-003
  Scenario: Park transform rotates correctly at known angle
    Given stationary frame currents alpha = 1.0 A, beta = 0.0 A
    And rotor electrical angle theta = 0 degrees
    When the Park transform is applied
    Then id = 1.0 A
    And iq = 0.0 A
