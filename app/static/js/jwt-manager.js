class JwtManager {
    constructor() {
        this.expiryKey = "jwt_expiry_time";
        this.checkIntervalMs = 60 * 1000; // 1 minute
        this.renewThresholdSec = 180; // 3 minutes
        this.intervalId = null;
    }

    async init() {
        let expiry = this.getStoredExpiry();
        if (!expiry) {
            expiry = await this.fetchTokenInfo();
        }
        if (expiry) {
            this.storeExpiry(expiry);
        }

        this.startMonitoring();
        this.checkRenewalNow();
    }

    startMonitoring() {
        if (this.intervalId) clearInterval(this.intervalId);

        this.intervalId = setInterval(async () => {
            const expiry = this.getStoredExpiry();
            if (!expiry) {
                // Missing info → attempt re-fetch
                await this.fetchTokenInfo();
                return;
            }

            const now = Math.floor(Date.now() / 1000);
            if (expiry - now < this.renewThresholdSec) {
                await this.fetchTokenInfo(true); // force renew
            }
        }, this.checkIntervalMs);
    }

    /**
     * Fetch token info (and renew if needed).
     * @param {boolean} renew 
     * @returns {number|null} expiry timestamp (seconds)
     */
    async fetchTokenInfo(renew = false) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 5000); // 5s timeout

        try {
            const url = tokenCheckUrl + (renew ? "?renew=1" : "");
            const resp = await fetch(url, {
                method: "GET",
                signal: controller.signal,
            });
            clearTimeout(timeout);

            if (!resp.ok) {
                console.warn("Token check failed with status:", resp.status);
                return null;
            }

            let data = null;
            try {
                data = await resp.json();
            } catch (jsonErr) {
                console.warn("Invalid or empty token response JSON");
                return null;
            }

            if (data && typeof data.exp === "number") {
                this.storeExpiry(data.exp);
                this.checkRenewalNow(); // immediate re-check
                return data.exp;
            } else {
                console.warn("Token response missing 'exp'");
            }
        } catch (err) {
            if (err.name === "AbortError") {
                console.warn("Token fetch request timed out");
            } else {
                console.error("Error fetching token info:", err);
            }
        } finally {
            clearTimeout(timeout);
        }

        return null;
    }

    storeExpiry(expiry) {
        localStorage.setItem(this.expiryKey, expiry.toString());
    }

    getStoredExpiry() {
        const val = localStorage.getItem(this.expiryKey);
        return val ? parseInt(val, 10) : null;
    }

    async checkRenewalNow() {
        const expiry = this.getStoredExpiry();
        if (!expiry) return;
        const now = Math.floor(Date.now() / 1000);
        if (expiry - now < this.renewThresholdSec) {
            await this.fetchTokenInfo(true);
        }
    }
}

