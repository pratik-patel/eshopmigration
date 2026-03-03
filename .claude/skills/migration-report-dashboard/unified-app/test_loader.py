#!/usr/bin/env python
"""Test data loader"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from lib.unified_loader import UnifiedDataLoader

try:
    loader = UnifiedDataLoader(docs_path='../../../docs', mock_legacy_path='../mock-data/legacy')
    print('[OK] Loader created')

    seams = loader.modern.get_all_seams()
    print(f'[OK] Seams: {seams}')

    score = loader.get_migration_health_score()
    print(f'[OK] Health score: {score}')

    print('\n[SUCCESS] All tests passed!')
except Exception as e:
    print(f'\n[ERROR] {e}')
    import traceback
    traceback.print_exc()
