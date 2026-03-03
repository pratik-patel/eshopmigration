#!/bin/bash
# Simple test script to simulate what Claude Code sends to hooks

# Simulate the JSON that Claude Code sends on stdin
TEST_JSON='{"session_id":"test","hook_event_name":"SubagentStart","agent_id":"test123","agent_type":"test-discovery-agent"}'

echo "Testing hook with JSON:"
echo "$TEST_JSON"
echo ""

# Test the FIXED hook
echo "$TEST_JSON" | .claude/hooks/log-agent-start-FIXED.sh

echo ""
echo "Check the last entry in migration-activity.jsonl:"
tail -1 docs/tracking/migration-activity.jsonl

echo ""
echo "Check debug log:"
tail -10 docs/tracking/hook-debug.log
