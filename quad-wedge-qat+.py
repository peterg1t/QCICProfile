def qw(energy, beamtype, machinetype, cart, measurement):

    # D10 and R50 IC Profiler Calibration Data Below.-------------------------
    # Cart A
    ic_profiler_calibration_A = {
        (6, "X", "truebeam"): (151.3453, -10.6672),
        (6, "FFF", "truebeam"): (184.138, -31.0792),
        (15, "X", "truebeam"): (117.088, 9.85158),
        (10, "X", "truebeam"): (98.1368, 19.7898),
        (10, "FFF", "truebeam"): (143.915, -9.83472),
        (6, "X", "clinac"): (151.3453, -10.7822),
        (10, "X", "clinac"): (98.1368, 19.8136),
        (6, "e", "truebeam"): (1603.73800, -537.15500, 47.14986),
        (9, "e", "truebeam"): (348.56370, -176.65700, 25.68557),
        (12, "e", "truebeam"): (142.14400, -109.24300, 25.71886),
        (16, "e", "truebeam"): (325.17690, -335.77100, 92.95582),
        (20, "e", "truebeam"): (734.65730, -873.04600, 267.15960),
    }

    # Cart B
    ic_profiler_calibration_B = {
        (6, "X", "truebeam"): (151.345, -10.7339),
        (6, "FFF", "truebeam"): (184.138, -31.7887),
        (15, "X", "truebeam"): (117.0881, 9.34063),
        (10, "X", "truebeam"): (98.1368, 19.4017),
        (10, "FFF", "truebeam"): (143.9148, -10.492),
        (6, "X", "clinac"): (151.345, -11.0944),
        (10, "X", "clinac"): (98.1368, 19.5740),
        (6, "e", "truebeam"): (1603.73800, -537.15500, 47.15816),
        (9, "e", "truebeam"): (348.56370, -176.65700, 25.68334),
        (12, "e", "truebeam"): (142.14400, -109.24300, 25.68339),
        (16, "e", "truebeam"): (325.17690, -335.77100, 92.84838),
        (20, "e", "truebeam"): (734.65730, -873.04600, 267.01717),
    }
    # End of calibration data. ------------------------------------------------

    if cart == "A":
        if beamtype == "e":
            C1 = ic_profiler_calibration_A[energy, beamtype, machinetype][0]
            C2 = ic_profiler_calibration_A[energy, beamtype, machinetype][1]
            C3 = ic_profiler_calibration_A[energy, beamtype, machinetype][2]
            return C1 * measurement * measurement + C2 * measurement + C3
        else:
            m = ic_profiler_calibration_A[energy, beamtype, machinetype][0]
            b = ic_profiler_calibration_A[energy, beamtype, machinetype][1]
            return m * measurement + b
    elif cart == "B":
        if beamtype == "e":
            C1 = ic_profiler_calibration_B[energy, beamtype, machinetype][0]
            C2 = ic_profiler_calibration_B[energy, beamtype, machinetype][1]
            C3 = ic_profiler_calibration_B[energy, beamtype, machinetype][2]
            return C1 * measurement * measurement + C2 * measurement + C3
        else:
            m = ic_profiler_calibration_B[energy, beamtype, machinetype][0]
            b = ic_profiler_calibration_B[energy, beamtype, machinetype][1]
            return m * measurement + b


energy = 10
beamtype = "X"
machinetype = "truebeam"
cart = _icprofiler_cart
area_ratio = _10x_qw_icp_upload_analysis["area_ratio"]

#_10x_D10 = qw(energy, beamtype, machinetype, cart, area_ratio)
_10x_D10 = qw(energy, beamtype, machinetype, cart, area_ratio)
