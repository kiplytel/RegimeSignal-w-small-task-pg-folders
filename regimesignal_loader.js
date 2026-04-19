/**
 * RegimeSignal Data Loader
 * ===========================================================
 * Drop <script src="regimesignal_loader.js"></script> into any
 * RegimeSignal page. Mark elements with data-rs attributes.
 * The loader fetches regimesignal_data.json and auto-populates.
 *
 * BASIC USAGE:
 *   <span data-rs="rts.composite">—</span>
 *   <span data-rs="mrs.composite" data-rs-decimals="1">—</span>
 *   <span data-rs="rts.change_30d" data-rs-signed="true">—</span>
 *   <span data-rs="validated_stats.bull_recovery_primary_pct"
 *         data-rs-suffix="%">—</span>
 *
 * CONDITIONAL DISPLAY:
 *   <div data-rs-show-if="rts.bull_recovery_signal"
 *        data-rs-equals="Active">Recovery Active!</div>
 *
 * ZONE COLORING (adds rs-zone-{green|yellow|amber|orange|red}):
 *   <div class="zone-badge" data-rs-color="mrs.zone_color">...</div>
 *
 * REPEATING LISTS (for factor rows, history table, etc.):
 *   <tbody data-rs-repeat="sub_core_factors"
 *          data-rs-template="factor-row-tmpl"></tbody>
 *   <template id="factor-row-tmpl">
 *     <tr><td>{{name}}</td><td>{{score}}</td></tr>
 *   </template>
 *
 * Every page that uses this loader updates automatically when
 * Python writes a new regimesignal_data.json. Zero hardcoded
 * values on the pages themselves.
 */

(function () {
    'use strict';

    const DATA_URL = 'regimesignal_data.json';
    const DEFAULT_FALLBACK = '—';

    // --- Path walker: supports "rts.stage_transition_probs.bear" ---
    function getPath(obj, path) {
        if (!obj || !path) return null;
        const parts = path.split('.');
        let cur = obj;
        for (const p of parts) {
            if (cur === null || cur === undefined) return null;
            cur = cur[p];
        }
        return cur;
    }

    // --- Format a value with the element's data-rs-* options ---
    function formatValue(val, el) {
        if (val === null || val === undefined || val === '') {
            return el.getAttribute('data-rs-fallback') || DEFAULT_FALLBACK;
        }

        const decimals = el.getAttribute('data-rs-decimals');
        const signed = el.getAttribute('data-rs-signed') === 'true';
        const prefix = el.getAttribute('data-rs-prefix') || '';
        const suffix = el.getAttribute('data-rs-suffix') || '';

        let out = val;

        if (typeof val === 'number') {
            if (decimals !== null && decimals !== undefined) {
                out = val.toFixed(parseInt(decimals, 10));
            }
            if (signed && val > 0) {
                out = '+' + out;
            }
        }

        return prefix + out + suffix;
    }

    // --- Main populator ---
    function populate(data) {
        // 1. Simple value binding
        document.querySelectorAll('[data-rs]').forEach(el => {
            const path = el.getAttribute('data-rs');
            const val = getPath(data, path);
            el.textContent = formatValue(val, el);
        });

        // 2. Zone color class binding
        document.querySelectorAll('[data-rs-color]').forEach(el => {
            const path = el.getAttribute('data-rs-color');
            const color = getPath(data, path);
            el.classList.remove(
                'rs-zone-green', 'rs-zone-yellow', 'rs-zone-amber',
                'rs-zone-orange', 'rs-zone-red',
                'rs-zone-purple', 'rs-zone-blue'
            );
            if (color) el.classList.add('rs-zone-' + color);
        });

        // 3. Conditional visibility
        document.querySelectorAll('[data-rs-show-if]').forEach(el => {
            const path = el.getAttribute('data-rs-show-if');
            const equals = el.getAttribute('data-rs-equals');
            const val = getPath(data, path);
            let visible = val !== null && val !== undefined && val !== '' && val !== false;
            if (equals !== null && equals !== undefined) {
                visible = String(val) === equals;
            }
            el.style.display = visible ? '' : 'none';
        });

        // 4. Meta-driven timestamp
        if (data._meta && data._meta.generated_at) {
            document.querySelectorAll('[data-rs-updated]').forEach(el => {
                try {
                    el.textContent = new Date(data._meta.generated_at).toLocaleString();
                } catch (e) { /* ignore */ }
            });
        }
    }

    // --- Repeating list renderer ---
    function renderRepeats(data) {
        document.querySelectorAll('[data-rs-repeat]').forEach(container => {
            const path = container.getAttribute('data-rs-repeat');
            const templateId = container.getAttribute('data-rs-template');
            const arr = getPath(data, path);
            if (!Array.isArray(arr)) return;
            const template = document.getElementById(templateId);
            if (!template) {
                console.warn('[RegimeSignal] template not found: ' + templateId);
                return;
            }

            container.innerHTML = '';
            arr.forEach((item, idx) => {
                let html = template.innerHTML;
                html = html.replace(/\{\{([\w_.]+)\}\}/g, (_, key) => {
                    const v = key === 'index' ? idx : getPath(item, key);
                    return v === null || v === undefined ? DEFAULT_FALLBACK : v;
                });
                const wrap = document.createElement('div');
                wrap.innerHTML = html.trim();
                while (wrap.firstChild) container.appendChild(wrap.firstChild);
            });
        });
    }

    // --- Init ---
    async function init() {
        try {
            const res = await fetch(DATA_URL, { cache: 'no-store' });
            if (!res.ok) throw new Error('HTTP ' + res.status);
            const data = await res.json();
            window.__regimesignal_data = data; // for debugging in console
            renderRepeats(data);
            populate(data);
            document.dispatchEvent(new CustomEvent('regimesignal:loaded', { detail: data }));
        } catch (err) {
            console.warn('[RegimeSignal] Could not load ' + DATA_URL + ':', err);
            console.warn('[RegimeSignal] Page will show fallback values. This is expected in local dev without a web server.');
            document.dispatchEvent(new CustomEvent('regimesignal:error', { detail: err }));
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose manual refresh
    window.regimesignalReload = init;
})();
