import math
from scipy.stats import norm

def bs_delta(S, K, T, r, sigma, option_type="call"):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    if option_type == "call":
        return norm.cdf(d1)
    else:
        return norm.cdf(d1) - 1

def bs_vega(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    return S * norm.pdf(d1) * math.sqrt(T)

def bs_implied_vol(price, S, K, T, r, option_type="call", tol=1e-5, max_iter=100):
    sigma = 0.2  # initial guess
    for i in range(max_iter):
        price_estimate = bs_price(S, K, T, r, sigma, option_type)
        vega = bs_vega(S, K, T, r, sigma)
        price_diff = price - price_estimate
        if abs(price_diff) < tol:
            return sigma
        sigma = sigma + price_diff / vega
    return sigma

def bs_price(S, K, T, r, sigma, option_type="call"):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if option_type == "call":
        price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return price
