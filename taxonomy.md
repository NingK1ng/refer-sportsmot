# Refer-SportsMOT Query Taxonomy

## Overview

Each referring expression in Refer-SportsMOT is labeled with one of five query types. The taxonomy is meant to reflect the kinds of language cues that are visible in team-sports tracking footage while remaining grounded in actual evidence.

## Query Types

### 1. Appearance
Describes visible visual attributes without relying on motion or landmark relations.

**Examples**
- `the player in the red jersey`
- `the white-shirted player`
- `the dark-uniform player on the left`

**Keep only if**
- the appearance cue is visible in the target crop
- the wording is supported by dominant color or clear clothing evidence

### 2. Jersey Number
References a visible jersey number.

**Examples**
- `the player wearing #10`
- `number 7 in white`
- `the player with jersey 23`

**Keep only if**
- OCR or strong visual evidence supports the number
- the number is not guessed from context

### 3. Spatial
Identifies the player through frame position or sport-specific landmarks.

**Examples**
- `the player near the left touchline`
- `the player by the right baseline`
- `the player closest to the center circle`

**Keep only if**
- the expression uses a legal landmark or stable positional cue
- the target is distinguishable from nearby players under that cue

### 4. Action
Describes a visible action or motion state.

**Examples**
- `the player running back`
- `the player shuffling to the right`
- `the player holding position near the net`

**Keep only if**
- the action is supported by the action strip or motion evidence
- the action is visible enough to separate the target from nearby players
- the expression does not guess ball possession or hidden intent

### 5. Composite
Combines at least two evidence sources.

**Examples**
- `the red jersey player near the right wing`
- `number 11 near the left touchline`
- `the white-shirted player running toward the baseline`

**Keep only if**
- at least two evidence dimensions are explicitly present
- the combined description is stronger than either cue alone

## Target Distribution

| Query Type | Target % |
|-----------|----------|
| Appearance | 25-30% |
| Jersey Number | 18-22% |
| Spatial | 22-26% |
| Action | 13-17% |
| Composite | 12-16% |

These are soft targets. Unsupported query types should be dropped rather than forced.
