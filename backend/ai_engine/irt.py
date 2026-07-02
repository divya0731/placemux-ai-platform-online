import math

# Quadrature points for EAP estimation
GRID_MIN = -4.0
GRID_MAX = 4.0
GRID_STEP = 0.1
QUAD_POINTS = [round(GRID_MIN + i * GRID_STEP, 2) for i in range(int((GRID_MAX - GRID_MIN) / GRID_STEP) + 1)]

# Standard normal prior probabilities for each quadrature point
def normal_pdf(x):
    return (1.0 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * x * x)

PRIORS = [normal_pdf(pt) for pt in QUAD_POINTS]

def probability_correct(theta: float, a: float, b: float, c: float) -> float:
    """
    3-Parameter Logistic (3PL) IRT Model.
    Calculates the probability of a correct response.
    theta: candidate ability
    a: discrimination parameter (steepness of curve)
    b: difficulty parameter (location)
    c: guessing parameter (lower asymptote)
    """
    exponent = -a * (theta - b)
    # Prevent overflow in exponential calculation
    exponent = max(-50.0, min(50.0, exponent))
    denom = 1.0 + math.exp(exponent)
    return c + (1.0 - c) / denom

def estimate_theta_eap(responses: list) -> tuple:
    """
    Expected A Posteriori (EAP) ability estimation.
    responses: list of dicts/objects having keys: 'is_correct', 'a_param', 'b_param', 'c_param'
    Returns: (theta_estimate, sem)
    """
    if not responses:
        # Return prior mean and standard deviation (0.0, 1.0) if no responses yet
        return 0.0, 1.0

    posteriors = []
    total_posterior_sum = 0.0

    for idx, pt in enumerate(QUAD_POINTS):
        # Calculate likelihood L(u | theta_j)
        likelihood = 1.0
        for r in responses:
            is_correct = r["is_correct"]
            a = r["a_param"]
            b = r["b_param"]
            c = r["c_param"]
            p = probability_correct(pt, a, b, c)
            likelihood *= p if is_correct else (1.0 - p)
        
        # Posterior = Likelihood * Prior
        post = likelihood * PRIORS[idx]
        posteriors.append(post)
        total_posterior_sum += post

    # If sum is zero (extremely rare numerical underflow), fallback to standard normal
    if total_posterior_sum == 0.0:
        return 0.0, 1.0

    # Normalize posteriors
    weights = [p / total_posterior_sum for p in posteriors]

    # Calculate expected value (mean) of theta
    theta_est = sum(w * pt for w, pt in zip(weights, QUAD_POINTS))

    # Calculate variance (standard deviation squared) of theta
    variance = sum(w * ((pt - theta_est) ** 2) for w, pt in zip(weights, QUAD_POINTS))
    sem = math.sqrt(variance)

    return theta_est, sem

def fisher_information(theta: float, a: float, b: float, c: float) -> float:
    """
    Calculates Fisher Information of an item at a given theta.
    Information is higher when item difficulty b matches theta, and when discrimination a is high.
    """
    p = probability_correct(theta, a, b, c)
    if p == 0.0 or p == 1.0:
        return 0.0
    
    numerator = (a ** 2) * (1.0 - p) * ((p - c) ** 2)
    denominator = p * ((1.0 - c) ** 2)
    
    if denominator == 0.0:
        return 0.0
        
    return numerator / denominator

# ── Stopping Rules ──────────────────────────────────────────────────────────

SEM_THRESHOLD = 0.30     # Stop when measurement precision is good enough
MIN_ITEMS     = 3        # Never stop before answering at least this many items
MAX_ITEMS     = 10       # Hard cap on total items regardless of SEM

def should_stop(responses: list, sem: float) -> tuple:
    """
    Evaluate CAT stopping criteria after each response.

    Returns: (stop: bool, reason: str)
    Stopping rules (in priority order):
      1. Hard maximum — always stop at MAX_ITEMS.
      2. SEM precision — stop when SEM < SEM_THRESHOLD and MIN_ITEMS answered.
      3. Item pool exhausted — handled by the caller.
    """
    n = len(responses)

    if n >= MAX_ITEMS:
        return True, f"max_items_reached ({MAX_ITEMS})"

    if n >= MIN_ITEMS and sem < SEM_THRESHOLD:
        return True, f"sem_threshold_met (SEM={round(sem, 3)} < {SEM_THRESHOLD})"

    return False, "continue"
