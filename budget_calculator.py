#!/usr/bin/env python3
import json

def calculate_phase_i_budget(total_award=150000.00):
    """
    Generates a structured SBIR Phase I budget allocation based on standard
    federal cost accounting principles and safe-harbor overhead thresholds.
    """
    allocation_ratios = {
        "Direct Senior Engineering Labor": 0.50,
        "Fringe Benefits & Payroll Tax": 0.10,
        "Materials & Validation Equipment": 0.15,
        "Indirect Costs & Overhead": 0.18,
        "Fixed Fee / Profit Margin": 0.07
    }
    
    budget_manifest = {
        "meta": {
            "total_funding_award": total_award,
            "currency": "USD",
            "compliance_status": "FAR_COMPLIANT"
        },
        "allocations": {}
    }
    
    for category, ratio in allocation_ratios.items():
        budget_manifest["allocations"][category] = {
            "percentage": f"{ratio * 100:.1f}%",
            "allocated_amount": round(total_award * ratio, 2)
        }
        
    return budget_manifest

if __name__ == "__main__":
    # Default SBIR Phase I Maximum Allocation Profile
    funding_profile = calculate_phase_i_budget(150000.00)
    print(json.dumps(funding_profile, indent=4))
  
