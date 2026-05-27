/**
 * Unit tests for the validation logic. Doesn't actually register Playwright
 * tests — that would require a browser. Runs under vitest.
 */

import { describe, expect, it } from 'vitest';

import { validateIntentArgs } from '../src/intent.js';

describe('validateIntentArgs', () => {
    it('accepts a single claim ID', () => {
        const ids = validateIntentArgs('INT-001', () => {});
        expect(ids).toEqual(['INT-001']);
    });

    it('accepts an array of claim IDs', () => {
        const ids = validateIntentArgs(['INT-001', 'INT-SB-002'], () => {});
        expect(ids).toEqual(['INT-001', 'INT-SB-002']);
    });

    it('accepts prefixed claim IDs (INT-SB-001, INT-WB-E01)', () => {
        expect(validateIntentArgs('INT-SB-001', () => {})).toEqual(['INT-SB-001']);
        expect(validateIntentArgs('INT-WB-E01', () => {})).toEqual(['INT-WB-E01']);
    });

    it('rejects an empty list', () => {
        expect(() => validateIntentArgs([], () => {})).toThrow('at least one claim ID');
    });

    it('rejects an invalid ID format', () => {
        expect(() => validateIntentArgs('BAD-001', () => {})).toThrow('claim ID must match');
        expect(() => validateIntentArgs('int-001', () => {})).toThrow('claim ID must match');
        expect(() => validateIntentArgs('INT001', () => {})).toThrow('claim ID must match');
    });

    it('requires a test body', () => {
        expect(() => validateIntentArgs('INT-001', undefined)).toThrow('requires a test body');
    });
});
