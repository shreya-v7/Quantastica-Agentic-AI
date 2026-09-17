# Trust center

Quantastica processes household books for a deploying bank or firm. The numbers
below are the running contract, not a SOC 2 report.

| Claim | Today |
|---|---|
| Residency | `asia-south1` planned. Local Postgres in tests and `make dev`. |
| CMEK | False. No customer-managed keys have been bound. |
| RLS | `document_chunks` policy uses `SET LOCAL app.current_user_id`. FORCE in the control-plane migration. |
| DSR | Access (adviser+) and erasure (admin). Audit rows retained. |
| Breach window | 72 hours, as stated in `/api/control/trust`. |
| Advice | Informational only. Not a SEBI-registered adviser. |
| Trading | Paper. Conversational trading is off until `TRADING_CHAT_ENABLED`. |
| Kernel | Sole source of rupees. Models classify, extract, and narrate. |

Machine-readable copy: `GET /api/control/trust`.
