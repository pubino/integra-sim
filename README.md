# Integration Simulator

[Run in your browser](https://pubino.github.io/integra-sim/).

The browser ports the original function, midpoint rectangle rule, and trapezoidal rule to Python.
Set the parameters and select **Integrate**. Use **Show on plot** to compare the methods together
or inspect either on its own. The interval can run in either direction, and the results are signed.
The browser accepts 1 to 1,000 panels.

Part of [Prof. Robert Vanderbei's Java Applications](https://pubino.github.io/vanderbei-apps#integra-sim).

An interactive Java application for visualizing numerical integration methods by Professor Robert Vanderbei, Princeton University (1997).

## Overview

This educational tool allows users to:
- Visualize numerical integration of parametric functions
- Compare Rectangle Rule vs Trapezoidal Rule approximations
- See how the number of intervals affects accuracy
- Understand the geometric interpretation of numerical integration

## Features

- **Parametric Function**: Integrates f(x) = a·x^k·exp(-x²/b)
- **Rectangle Rule**: Mid-point approximation (shown in yellow)
- **Trapezoidal Rule**: Linear interpolation (shown in red)
- **Exact Curve**: High-resolution function plot (shown in blue)
- **Computed Areas**: Displays numerical results for both methods

## Requirements

- Java 14+ (for running the JAR)
- Java 14+ with `jpackage` (for building macOS app bundle)

## Building

```bash
# Build the JAR file
make jar

# Build macOS .app bundle (unsigned)
make app
```

## Running

```bash
# Run the JAR
make run

# Or run directly
java -jar dist/IntegraSim.jar
```

## Usage

### Setting Parameters

1. **Function parameters**:
   - **a**: Amplitude coefficient (default: 1)
   - **b**: Width parameter in exponential (default: 2)
   - **k**: Power of x (default: 0, giving a Gaussian)

2. **Integration bounds**:
   - **Low x**: Lower integration limit (default: -3)
   - **High x**: Upper integration limit (default: 3)

3. **Resolution**:
   - **n**: Number of intervals (default: 10)

4. Click **Integrate** to compute and visualize

### Visual Elements

- **Yellow rectangles**: Rectangle rule approximation (mid-point)
- **Red trapezoids**: Trapezoidal rule approximation
- **Blue curve**: Accurate function plot (1000 points)
- **Green lines**: X and Y axes
- **White text**: Computed area values for both methods

## Project Structure

```
integra-sim/
├── integra/
│   └── Integra.java        # Main app and IntegrationCanvas
├── myutil/
│   ├── AppletFrame.java    # Applet-to-Frame wrapper
│   ├── GL.java             # Graphics library utilities
│   ├── SL.java             # String parsing utilities
│   ├── GridPanel.java      # Grid layout panel
│   └── Format.java         # Number formatting
├── Makefile                # Build configuration
└── .github/workflows/      # CI/CD configuration
```

## Numerical Methods

### Rectangle Rule (Mid-point)
Approximates the integral using rectangles with heights evaluated at interval midpoints:

∫f(x)dx ≈ Σ f(xᵢ + Δx/2) · Δx

This is a second-order method (error ~ O(Δx²)).

### Trapezoidal Rule
Approximates the integral using trapezoids:

∫f(x)dx ≈ Δx · [f(x₀)/2 + f(x₁) + f(x₂) + ... + f(xₙ)/2]

Also a second-order method, but with different error characteristics.

## Example Functions

**Gaussian (k=0)**:
- a=1, b=2, k=0
- Integrates exp(-x²/2), related to normal distribution

**Odd function (k=1)**:
- a=1, b=2, k=1
- Integral over symmetric bounds equals 0

**Even function (k=2)**:
- a=1, b=2, k=2
- Related to moments of Gaussian distribution

## Experiments

1. **Accuracy vs n**: Increase n to see convergence
2. **Odd functions**: Set k=1 to see cancellation
3. **Narrow peaks**: Decrease b to make sharper peaks
4. **Compare methods**: Notice when rectangle vs trapezoidal differs

## Browser development

Preview the static page locally using Docker or Python 3.13 with uv.

```sh
docker-compose up --build preview
# Or build and serve directly
uv sync --locked
uv run python scripts/build_site.py
uv run python -m http.server 8000 --bind 127.0.0.1 --directory build/site
```

Run the Java parity tests, Chromium tests, and lint and type checks used in CI.

```sh
docker-compose run --build --rm -T js-check
docker-compose run --build --rm -T test
```
