---
title: FOC Architecture
type: architecture
status: draft
version: "1.0"
component: foc
---

## Assumptions & Constraints

No heap allocation. All buffers are statically allocated.
The FOC loop must complete within 400 cycles at 120 MHz.

## System Overview

Field-Oriented Control (FOC) provides independent torque and flux control
for BLDC/PMSM motors by transforming phase currents into a rotating frame
aligned with the rotor flux.

## Component Decomposition

- Clarke transform: converts 3-phase currents to alpha-beta frame
- Park transform: rotates to rotor-synchronous d-q frame
- PI controllers: independent Id and Iq regulators
- Inverse Park and SVM: reconstruct phase voltages

## Interfaces & Contracts

All interfaces are defined as pure abstract classes. Platform-specific
implementations are injected via the `PlatformFactory` interface.
