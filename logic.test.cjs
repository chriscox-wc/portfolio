const test = require('node:test');
const assert = require('node:assert/strict');
const {sortFrames, matches, shuffle} = require('../dist/logic.js');
const {entries} = require('../content.json');

test('insertion sort handles arbitrary order, duplicates, negatives, and empty input', () => {
  for (const values of [[],[3],[1,2,3],[3,2,1],[4,4,1,-2,1],[62,28,84,16,47,93,36,72,54,22,81,41]]) {
    const original = values.slice();
    const frames = sortFrames(values);
    assert.deepEqual(values, original);
    assert.deepEqual(frames.at(-1).values, values.slice().sort((a,b)=>a-b));
    assert.equal(frames.at(-1).done, true);
    for (const frame of frames) {
      assert.deepEqual(frame.values.slice().sort((a,b)=>a-b), original.slice().sort((a,b)=>a-b));
      assert.ok(frame.active.every(i=>i>=0&&i<values.length));
    }
  }
});
test('counts distinguish already sorted and reversed values', () => {
  assert.equal(sortFrames([1,2,3,4]).at(-1).comparisons,3);
  assert.equal(sortFrames([1,2,3,4]).at(-1).swaps,0);
  const reverse = sortFrames([4,3,2,1]).at(-1);
  assert.equal(reverse.comparisons,6);
  assert.equal(reverse.swaps,6);
});
test('CV search handles categories, multiple words, case, and empty results', () => {
  assert.equal(entries.filter(e=>matches(e,'Experience','')).length,6);
  const chapter=entries.filter(e=>matches(e,'All','  DC COMICS  '));
  assert.equal(chapter.length,1);
  assert.match(chapter[0].status,/Accepted proposal/);
  assert.equal(entries.filter(e=>matches(e,'Education','DC')).length,0);
  assert.ok(entries.some(e=>matches(e,'All','web developer')));
  assert.equal(entries.filter(e=>matches(e,'All','zzzzzzz')).length,0);
  assert.ok(entries.some(e=>matches(e,'Education','not yet enrolled')));
  assert.equal(matches(entries[0],'All','AI'),false,'AI should not match chair');
});
test('shuffle preserves values and does not change its input', () => {
  const input=[1,2,3,4,5]; const result=shuffle(input,()=>0);
  assert.deepEqual(input,[1,2,3,4,5]);
  assert.deepEqual(result.slice().sort(),input);
  assert.notDeepEqual(result,input);
});
