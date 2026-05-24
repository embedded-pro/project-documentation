---
title: Clarke Transform Design
type: design
status: approved
version: "1.0"
component: foc
---

## Responsibilities

Convert three-phase stator currents (ia, ib, ic) to the two-phase
stationary reference frame (alpha, beta) using the power-invariant form.

## Component Details

The Clarke transform is implemented as a static inline function operating
on Q31 fixed-point values. The coefficients are precomputed as compile-time
constants to avoid runtime division.

## Interfaces

Input: `ia`, `ib` (ic is derived from Kirchhoff's current law: ic = -ia - ib).
Output: `alpha = ia`, `beta = (ia + 2*ib) / sqrt(3)`.
