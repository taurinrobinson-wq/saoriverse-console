"""
Styling Utilities and Defensive JavaScript Injection.

Provides reusable styling utilities and defensive DOM patches for
jQuery compatibility and DOM safety.
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)


def inject_defensive_scripts() -> None:
    """Inject defensive JavaScript for jQuery compatibility.

    Patches jQuery to handle null/undefined selectors during theme toggles
    and adds error overlays for unhandled exceptions.
    """
    # jQuery patch for theme toggles
    try:
        st.markdown(
            """
            <script>
            (function(){
                try{
                    var jq = window.jQuery || window.$;
                    if(!jq || !jq.fn) return;
                    // Patch jQuery.fn.init to coerce null/undefined selectors to
                    // an empty string so Sizzle doesn't throw the TypeError when
                    // called with invalid arguments during theme toggles.
                    try{
                        var _origInit = jq.fn.init;
                        if(typeof _origInit === 'function'){
                            jq.fn.init = function(selector, context, root){
                                try{
                                    if(selector === null || typeof selector === 'undefined'){
                                        selector = '';
                                    }
                                    return _origInit.call(this, selector, context, root);
                                }catch(e){
                                    try{
                                        return _origInit.call(this, '');
                                    }catch(e2){
                                        return _origInit.apply(this, arguments);
                                    }
                                }
                            };
                        }
                    }catch(e){/* swallow */}
                }catch(e){/* swallow */}
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        logger.debug(f"Error injecting jQuery patch: {e}")


def inject_error_overlay() -> None:
    """Inject error overlay for unhandled client-side errors.

    Displays errors in a fixed overlay so users and developers can see
    what went wrong during theme toggles or other DOM operations.
    """
    try:
        st.markdown(
            """
            <script>
            (function(){
                try{
                    function showErrorOverlay(msg){
                        try{
                            var id = 'fp-client-error-overlay';
                            var existing = document.getElementById(id);
                            if(existing) existing.remove();
                            var el = document.createElement('div');
                            el.id = id;
                            el.style.position = 'fixed';
                            el.style.right = '12px';
                            el.style.top = '12px';
                            el.style.zIndex = 999999;
                            el.style.maxWidth = 'min(90vw,800px)';
                            el.style.background = 'rgba(255,255,255,0.95)';
                            el.style.color = '#111';
                            el.style.border = '1px solid #e33';
                            el.style.padding = '12px';
                            el.style.borderRadius = '8px';
                            el.style.boxShadow = '0 6px 24px rgba(0,0,0,0.2)';
                            var pre = document.createElement('pre');
                            pre.style.maxHeight = '40vh';
                            pre.style.overflow = 'auto';
                            pre.style.whiteSpace = 'pre-wrap';
                            pre.style.fontSize = '12px';
                            pre.textContent = msg;
                            el.appendChild(pre);
                            var btn = document.createElement('button');
                            btn.textContent = 'Dismiss';
                            btn.style.marginTop = '8px';
                            btn.onclick = function(){ el.remove(); };
                            el.appendChild(btn);
                            document.body.appendChild(el);
                        }catch(e){/*ignore*/}
                    }

                    window.addEventListener('error', function(ev){
                        try{
                            var m = ev && ev.error && ev.error.stack ? ev.error.stack : (ev && ev.message) || String(ev);
                            showErrorOverlay(m);
                        }catch(e){}
                    }, true);

                    window.addEventListener('unhandledrejection', function(ev){
                        try{
                            var m = ev && ev.reason && ev.reason.stack ? ev.reason.stack : JSON.stringify(ev.reason);
                            showErrorOverlay('UnhandledPromiseRejection: ' + m);
                        }catch(e){}
                    }, true);
                }catch(e){}
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        logger.debug(f"Error injecting error overlay: {e}")


def inject_container_styles() -> None:
    """Inject container and layout styling for splash screen.

    Reduces top padding and ensures proper alignment for main content.
    """
    try:
        st.markdown(
            """
            <style>
            /* Reduce top spacing so main content aligns with sidebar */
            .block-container {
                padding-top: 0.6rem !important;
            }
            /* Ensure chat area and inputs sit flush with sidebar headers */
            .streamlit-expanderHeader, .streamlit-expanderContent {
                margin-top: 0 !important;
                padding-top: 0 !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        logger.debug(f"Error injecting container styles: {e}")


def inject_splash_css() -> None:
    """Inject CSS for splash screen layout."""
    try:
        st.markdown(
            """
            <style>
            .splash-logo-container {
                text-align: center;
                margin-bottom: 2rem;
                margin-top: 0.4rem !important;
            }
            #fp-top-header {
                position: sticky;
                top: 0;
                z-index: 9999;
                background: var(--spacer, transparent);
                padding: 0.5rem 0;
                margin-bottom: 0.25rem;
            }
            .splash-logo {
                width: 200px;
                height: auto;
                margin-bottom: 1rem;
            }
            .splash-title {
                font-size: 2rem;
                font-weight: 300;
                letter-spacing: 0.2em;
                color: #2E2E2E;
                margin: 1rem 0 0.5rem 0;
                text-align: center;
                line-height: 1.2;
            }
            .splash-subtitle {
                font-size: 1.2rem;
                color: #666;
                letter-spacing: 0.1em;
                font-weight: 300;
                text-transform: uppercase;
                text-align: center;
                line-height: 1.5;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        logger.debug(f"Error injecting splash CSS: {e}")


def inject_svg_styling() -> None:
    """Inject CSS for SVG logo handling across themes."""
    try:
        st.markdown(
            """
            <style>
            /* Ensure inline SVGs in the brand/logo area inherit color from text */
            .brand-logo svg, .logo-container svg { fill: currentColor !important; }
            .splash-logo svg * { fill: currentColor !important; stroke: none !important; }

            /* Stronger splash CSS for inline SVG elements */
            .splash-logo, .splash-logo img, .splash-logo svg {
                display: block;
                margin: 0 auto;
                width: 140px;
                height: auto;
            }

            /* Force fills and remove strokes inside inline SVGs */
            .splash-logo svg * { fill: #31333F !important; stroke: none !important; }
            .splash-logo svg [fill="#fff"], .splash-logo svg [fill="#FFFFFF"] {
                fill: #31333F !important;
            }

            /* Improve rendering quality */
            .splash-logo svg {
                shape-rendering: geometricPrecision;
                image-rendering: optimizeQuality;
            }

            /* For <img> rendered SVGs, apply drop-shadow */
            .splash-logo img, img.splash-logo {
                filter: drop-shadow(0 0 6px rgba(0,0,0,0.25)) !important;
                background-color: transparent !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        logger.debug(f"Error injecting SVG styling: {e}")


def inject_sidebar_constraints() -> None:
    """Inject CSS to constrain sidebar width for form fields."""
    try:
        st.markdown(
            """
            <style>
            /* Constrain sidebar width */
            [data-testid="stSidebar"] > div {
                min-width: 260px !important;
                max-width: 400px !important;
            }
            /* Hide the vertical resize handle if present (best-effort) */
            .css-1v3fvcr { resize: none !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        logger.debug(f"Error injecting sidebar constraints: {e}")
