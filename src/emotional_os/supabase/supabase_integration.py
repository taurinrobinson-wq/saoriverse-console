"""Compatibility shim for supabase integration used in tests.

Re-export the implementation from the `tools` helper so tests importing
`emotional_os.supabase.supabase_integration` receive the expected symbols.
"""

from tools.supabase_integration import (
	SaoriResponse,
	SupabaseIntegrator,
	HybridEmotionalProcessor,
	create_supabase_integrator,
	create_hybrid_processor,
	create_local_processor,
)

__all__ = [
	"SaoriResponse",
	"SupabaseIntegrator",
	"HybridEmotionalProcessor",
	"create_supabase_integrator",
	"create_hybrid_processor",
	"create_local_processor",
]