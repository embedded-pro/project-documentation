---
title: FOC Theory
type: theory
status: approved
version: "1.0"
component: foc
---

## Overview

Field-Oriented Control (FOC) decouples torque and flux control in BLDC and PMSM
motors by transforming the phase currents into a rotating reference frame aligned
with the rotor flux.

## Mathematical Foundation

The Clarke transform converts three-phase currents to the stationary
two-phase (alpha-beta) reference frame:

$$i_\alpha = i_a, \quad i_\beta = \frac{1}{\sqrt{3}}(i_a + 2 i_b)$$

The Park transform rotates the stationary frame to the rotor-synchronous
rotating frame:

$$i_d = i_\alpha \cos\theta + i_\beta \sin\theta$$
$$i_q = -i_\alpha \sin\theta + i_\beta \cos\theta$$

## Numerical Properties

All transforms are implemented using 32-bit fixed-point (Q31) arithmetic to
avoid floating-point hardware requirements on low-cost targets.
