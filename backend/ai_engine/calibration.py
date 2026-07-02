import math

def calibrate_item_difficulties(response_matrix: list, initial_difficulties: dict, iterations=10) -> dict:
    """
    Performs simplified Joint Maximum Likelihood Estimation (JMLE) calibration.
    response_matrix: list of dicts, e.g. [{"candidate_id": 1, "responses": {"Q001": True, "Q002": False, ...}}]
    initial_difficulties: dict mapping question_id to initial b_param (difficulty)
    Returns: dict mapping question_id to calibrated b_param (difficulty)
    """
    # Unique questions and candidates
    question_ids = list(initial_difficulties.keys())
    candidate_ids = [r["candidate_id"] for r in response_matrix]
    
    # Initialize parameters
    # a_param fixed at 1.0, c_param fixed at 0.0 for basic calibration
    a_fixed = 1.0
    c_fixed = 0.0
    
    b_params = {q_id: diff for q_id, diff in initial_difficulties.items()}
    theta_estimates = {c_id: 0.0 for c_id in candidate_ids}

    # Calibration loop
    for iteration in range(iterations):
        # Step 1: Update candidate abilities (thetas) based on current item parameters
        for cand_record in response_matrix:
            c_id = cand_record["candidate_id"]
            cand_responses = cand_record["responses"]
            
            # Formulate local response array to feed EAP estimator
            local_responses = []
            for q_id, is_correct in cand_responses.items():
                if q_id in b_params:
                    local_responses.append({
                        "is_correct": is_correct,
                        "a_param": a_fixed,
                        "b_param": b_params[q_id],
                        "c_param": c_fixed
                    })
            
            # Simple EAP or MLE theta update
            if local_responses:
                # Basic MLE update for theta: theta = logit(success_rate)
                correct_count = sum(1 for r in local_responses if r["is_correct"])
                total_count = len(local_responses)
                
                # Clamp to avoid inf
                success_rate = max(0.1, min(0.9, correct_count / total_count))
                theta_estimates[c_id] = math.log(success_rate / (1.0 - success_rate))

        # Step 2: Update item difficulties (b_params) based on current candidate abilities (thetas)
        for q_id in question_ids:
            item_responses = []
            for cand_record in response_matrix:
                c_id = cand_record["candidate_id"]
                cand_responses = cand_record["responses"]
                if q_id in cand_responses:
                    item_responses.append({
                        "theta": theta_estimates[c_id],
                        "is_correct": cand_responses[q_id]
                    })
            
            if not item_responses:
                continue
                
            # Update b_param using Newton-Raphson approximation
            # Target is to solve: sum_j (u_j - P(theta_j | b_i)) = 0
            b_current = b_params[q_id]
            for _ in range(3): # inner NR iterations
                g_diff = 0.0  # Gradient
                h_diff = 0.0  # Hessian
                
                for resp in item_responses:
                    theta = resp["theta"]
                    u = 1.0 if resp["is_correct"] else 0.0
                    
                    # Probability correct
                    exponent = -a_fixed * (theta - b_current)
                    exponent = max(-50.0, min(50.0, exponent))
                    p = 1.0 / (1.0 + math.exp(exponent))
                    
                    g_diff += (u - p)
                    h_diff -= p * (1.0 - p)
                
                if h_diff == 0.0:
                    break
                
                # Update: b_new = b_old - gradient / Hessian (note minus signs)
                # Since dP/db has an extra minus sign, the standard NR correction is:
                adjustment = g_diff / h_diff
                b_current += max(-1.0, min(1.0, adjustment)) # clamp updates to stabilize

            b_params[q_id] = round(b_current, 3)

    return b_params

# Demonstration script run for verification
if __name__ == "__main__":
    # Test dataset: 5 items, 4 candidates
    demo_items = {"Q001": 0.0, "Q002": -0.5, "Q003": 0.5, "Q004": 1.0, "Q005": -1.0}
    demo_responses = [
        {"candidate_id": 1, "responses": {"Q001": True, "Q002": True, "Q003": False, "Q004": False, "Q005": True}},
        {"candidate_id": 2, "responses": {"Q001": True, "Q002": True, "Q003": True, "Q004": True, "Q005": True}},
        {"candidate_id": 3, "responses": {"Q001": False, "Q002": False, "Q003": False, "Q004": False, "Q005": False}},
        {"candidate_id": 4, "responses": {"Q001": True, "Q002": True, "Q003": False, "Q004": False, "Q005": True}}
    ]
    
    calibrated = calibrate_item_difficulties(demo_responses, demo_items)
    print("Pre-calibrated difficulties:", demo_items)
    print("Calibrated difficulties:", calibrated)
