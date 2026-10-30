#include <iostream>
#include <chrono>
#include <cmath>

// Force strict standard C linkage signatures to avoid method name mangling
extern "C" {

    /**
     * Executes low-level telemetry math calculations natively.
     * Includes exception handling boundaries to insulate the core runtime thread.
     * 
     * @param operational_mode Integer flag defining active hardware profiling matrix.
     * @return double Precise loop processing latency metric in microseconds.
     */
    double execute_hardware_loop(int operational_mode) {
        // 1. Input Sanitization Boundary
        if (operational_mode < 0 || operational_mode > 100) {
            std::cerr << "[ERROR] Hardware execution argument out of bounds: " << operational_mode << std::endl;
            return -1.0; 
        }

        // 2. High-Resolution Performance Clock Capture
        auto start_time = std::chrono::high_resolution_clock::now();

        try {
            // Simulated heavy numerical telemetry computation
            double matrix_accumulator = 0.0;
            int loop_bounds = 5000 * (operational_mode + 1);
            
            for (int i = 0; i < loop_bounds; ++i) {
                // Perform complex tracking operations
                matrix_accumulator += std::sin(i) * std::cos(i);
            }
            
            // Prevent compiler from optimization-stripping out an unused loop matrix variables
            if (matrix_accumulator == 999999.9) {
                std::cout << "[DEBUG] Threshold triggered: " << matrix_accumulator << std::endl;
            }
        }
        catch (const std::exception& error) {
            std::cerr << "[CRITICAL] Native hardware computational variance isolated: " << error.what() << std::endl;
            return -2.0;
        }
        catch (...) {
            std::cerr << "[CRITICAL] Unhandled low-level hardware register panic intercepted." << std::endl;
            return -3.0;
        }

        auto end_time = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::micro> processing_latency = end_time - start_time;

        return processing_latency.count();
    }
}
