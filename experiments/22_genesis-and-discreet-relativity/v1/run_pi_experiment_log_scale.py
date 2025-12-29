"""
Logarithmic Scale Pi Drift Test
================================

Test pi measurement at discrete logarithmic radius values with integer quantization.
Radii: 1, 10, 100, 1000, 10000, 100000, 1000000
"""

import math
from ..shared.substrate import SubstrateState
from ..shared.experiment import create_circle_initial_state
from ..shared.observers.pi_drift import PiDriftObserver


def create_quantized_circle(num_points: int, radius: float) -> SubstrateState:
    """
    Create a circle at given radius with INTEGER QUANTIZATION.

    Positions are rounded to nearest integer lattice point.
    """
    state = SubstrateState()

    # Place entities on a perfect circle, then
    # quantize
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points

        # Continuous position
        x_cont = radius * math.cos(angle)
        y_cont = radius * math.sin(angle)

        # QUANTIZE to integer lattice
        x = float(round(x_cont))
        y = float(round(y_cont))
        z = 0.0

        state.entities[i] = {}
        state.positions[i] = (x, y, z)
        state.adjacency.add_node(i)

    # Connect adjacent points on circle
    for i in range(num_points):
        next_i = (i + 1) % num_points
        state.adjacency.add_edge(i, next_i)

    return state


def measure_pi_at_radius(radius: float, num_points: int = 1000):
    """Measure pi at a specific radius with discrete quantization."""

    # Create quantized circle
    state = create_quantized_circle(num_points, radius)

    # Create observer
    observer = PiDriftObserver(max_radius=int(radius * 2), log_interval=1, output_dir=None)

    # Manually call observer to measure pi
    state.tick = 1  # Fake tick value
    observer.on_post_tick(state)

    # Extract pi measurement
    pi_history = observer.memory["pi_history"]

    # Find the radius bucket
    measured_radius = None
    pi_estimate = None
    for r, history in pi_history.items():
        if history:  # Has measurements
            measured_radius = r
            pi_estimate = history[0]
            break

    return measured_radius, pi_estimate


def check_float_precision(radius):
    """
    Check if float precision is sufficient at this radius.

    Returns the spacing between adjacent representable floats at this scale.
    If spacing > 1, integer quantization becomes meaningless.
    """
    import sys
    import math

    # Get the spacing between adjacent floats at this magnitude
    # Using numpy.spacing equivalent
    if radius == 0:
        return sys.float_info.min

    # Get the exponent of the radius
    exp = math.floor(math.log2(abs(radius)))
    # Spacing is 2^(exp - 52) for double precision (53 bits mantissa)
    spacing = 2.0 ** (exp - 52)

    return spacing


def main():
    """Test pi measurement at logarithmic radius scales - push to Python limits."""

    NUM_POINTS = 1000
    OUTPUT_CSV = "results/pi_drift_extreme_log_scale.csv"

    # Generate logarithmic radii: 10^0, 10^1, 10^2, ..., up to overflow
    # Python float max is approximately 1.7e+308
    RADII = []
    exponent = 0
    max_exponent = 308  # Push to Python's float limit

    while exponent <= max_exponent:
        try:
            radius = 10.0 ** exponent
            if math.isinf(radius):
                print(f"\nReached infinity at 10^{exponent}")
                break
            RADII.append(radius)
        except OverflowError:
            print(f"\nOverflow at 10^{exponent}")
            break

        # Logarithmic stepping with more points at extreme scales
        if exponent < 3:
            exponent += 1
        elif exponent < 10:
            exponent += 3
        elif exponent < 30:
            exponent += 5
        elif exponent < 100:
            exponent += 10
        elif exponent < 200:
            exponent += 20
        else:
            exponent += 50

    print("=" * 100)
    print("Pi Measurement at Extreme Logarithmic Radius Scales - ABSOLUTE PYTHON LIMITS")
    print("=" * 100)
    print(f"Points on circle: {NUM_POINTS}")
    print(f"Quantization: Integer lattice (positions rounded to nearest integer)")
    print(f"Testing radii from 10^0 to 10^{max_exponent} (or until overflow)")
    print(f"Output CSV: {OUTPUT_CSV}")
    print(f"")
    print(f"NOTE: Float precision becomes limiting factor when spacing between")
    print(f"      representable floats exceeds 1.0 (quantization becomes meaningless)")
    print(f"")
    print(f"{'Radius':<20} {'Float Spacing':<15} {'Pi Estimate':<18} {'Error':<15} {'Precision':<12}")
    print("-" * 100)

    results = []

    precision_loss_warning_shown = False

    for radius in RADII:
        try:
            # Check float precision at this scale
            float_spacing = check_float_precision(radius)

            measured_r, pi_est = measure_pi_at_radius(radius, NUM_POINTS)

            if pi_est is not None:
                error = abs(pi_est - math.pi)
                error_pct = (error / math.pi) * 100

                # Format radius in scientific notation for large values
                if radius >= 1e10:
                    radius_str = f"{radius:.2e}"
                else:
                    radius_str = f"{radius:.0f}"

                # Format float spacing
                if float_spacing >= 1.0:
                    spacing_str = f"{float_spacing:.2e}"
                    precision_status = "DEGRADED"
                    if not precision_loss_warning_shown:
                        print(f"\n*** WARNING: Float precision loss detected! Spacing = {float_spacing:.2e} ***\n")
                        precision_loss_warning_shown = True
                elif float_spacing >= 0.01:
                    spacing_str = f"{float_spacing:.2e}"
                    precision_status = "OK"
                else:
                    spacing_str = f"{float_spacing:.2e}"
                    precision_status = "EXCELLENT"

                print(f"{radius_str:<20} {spacing_str:<15} {pi_est:<18.10f} {error:<15.2e} {precision_status:<12}")

                results.append({
                    'target_radius': radius,
                    'measured_radius': measured_r,
                    'pi_estimate': pi_est,
                    'error': error,
                    'error_pct': error_pct,
                    'float_spacing': float_spacing,
                    'precision_status': precision_status
                })
            else:
                radius_str = f"{radius:.2e}" if radius >= 1e10 else f"{radius:.0f}"
                spacing_str = f"{float_spacing:.2e}"
                print(f"{radius_str:<20} {spacing_str:<15} {'N/A':<18} {'N/A':<15} {'N/A':<12}")

        except (OverflowError, ValueError) as e:
            radius_str = f"{radius:.2e}" if radius >= 1e10 else f"{radius:.0f}"
            print(f"{radius_str:<20} ERROR: {str(e)[:70]}")
            print(f"\nStopped at radius {radius:.2e} due to numerical error.")
            break

    print("=" * 80)
    print(f"")
    print(f"True pi: {math.pi:.15f}")
    print(f"Number of successful measurements: {len(results)}")
    print(f"")

    # Analyze trend
    if len(results) >= 2:
        print("ANALYSIS:")
        r0 = results[0]['target_radius']
        rN = results[-1]['target_radius']
        r0_str = f"{r0:.2e}" if r0 >= 1e6 else f"{r0:.0f}"
        rN_str = f"{rN:.2e}" if rN >= 1e6 else f"{rN:.0f}"

        print(f"  - Smallest radius ({r0_str}): Error = {results[0]['error_pct']:.4f}%")
        print(f"  - Largest radius ({rN_str}): Error = {results[-1]['error_pct']:.4f}%")

        error_ratio = results[0]['error_pct'] / max(results[-1]['error_pct'], 1e-10)
        print(f"  - Error reduction: {error_ratio:.1f}x")

        # Check for systematic drift
        pi_values = [r['pi_estimate'] for r in results]
        pi_trend = pi_values[-1] - pi_values[0]
        print(f"  - Pi trend (largest - smallest): {pi_trend:+.6f}")

        # Calculate min/max pi across all scales
        pi_min = min(pi_values)
        pi_max = max(pi_values)
        pi_range = pi_max - pi_min
        print(f"  - Pi range across all scales: {pi_min:.6f} to {pi_max:.6f} (range: {pi_range:.6f})")

        if abs(pi_trend) < 0.01:
            print(f"  - RESULT: No systematic pi drift detected")
        else:
            print(f"  - RESULT: Possible systematic drift of {pi_trend:+.6f}")

        print(f"\n  Scale ratio tested: {rN/r0:.2e}x")

    # Write results to CSV
    import csv
    import os

    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)

    with open(OUTPUT_CSV, 'w', newline='') as csvfile:
        fieldnames = ['log10_radius', 'target_radius', 'measured_radius', 'pi_estimate',
                     'pi_error', 'error_percent', 'float_spacing', 'precision_status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in results:
            import math as m
            log10_r = m.log10(result['target_radius'])
            writer.writerow({
                'log10_radius': log10_r,
                'target_radius': result['target_radius'],
                'measured_radius': result['measured_radius'],
                'pi_estimate': result['pi_estimate'],
                'pi_error': result['error'],
                'error_percent': result['error_pct'],
                'float_spacing': result['float_spacing'],
                'precision_status': result['precision_status']
            })

    print(f"\n{'='*100}")
    print(f"Results saved to: {OUTPUT_CSV}")
    print(f"Total measurements: {len(results)}")

    # Precision analysis
    degraded_results = [r for r in results if r['precision_status'] == 'DEGRADED']
    if degraded_results:
        print(f"\n PRECISION WARNING:")
        print(f"  - {len(degraded_results)} measurements with degraded precision (float spacing >= 1.0)")
        print(f"  - First degradation at R = {degraded_results[0]['target_radius']:.2e}")
        print(f"  - At this scale, integer quantization becomes meaningless due to float limits")
        print(f"  - Pi measurements beyond this point may not reflect true geometric drift")
    else:
        print(f"\n All measurements maintained excellent precision!")

    print(f"{'='*100}")


if __name__ == "__main__":
    main()
