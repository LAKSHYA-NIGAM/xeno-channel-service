"""
Message Template Variable Interpolator
Substitutes double-curly placeholders (e.g. {{first_name}}, {{order.id}}) with payload data,
supporting default fallbacks (e.g. {{name|Valued Customer}}).
"""

import re
from typing import Dict, Any


def interpolate_template(template_str: str, context: Dict[str, Any]) -> str:
  if not template_str or not isinstance(template_str, str):
    return ''

  def replace_placeholder(match):
    expression = match.group(1).strip()
    parts = expression.split('|')
    key_path = parts[0].strip()
    fallback = parts[1].strip() if len(parts) > 1 else ''

    # Lookup key or nested dot path in context
    current = context
    for key in key_path.split('.'):
      if isinstance(current, dict) and key in current:
        current = current[key]
      else:
        return fallback

    return str(current) if current is not None else fallback

  # Pattern: {{ key_path }} or {{ key_path | fallback }}
  pattern = re.compile(r'\{\{\s*([^}]+?)\s*\}\}')
  return pattern.sub(replace_placeholder, template_str)
