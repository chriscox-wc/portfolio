(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PortfolioLogic = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const normalize = value => String(value).toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '');
  function matches(entry, category, query) {
    const haystack = normalize([entry.title, entry.org, entry.text, entry.date, entry.status || '', ...entry.tags].join(' '));
    return (category === 'All' || entry.category === category) && normalize(query).trim().split(/\s+/).every(term => {
      if (/^[a-z0-9]{1,2}$/.test(term)) return new RegExp(`(^|[^a-z0-9])${term}([^a-z0-9]|$)`).test(haystack);
      return haystack.includes(term);
    });
  }
  function sortFrames(input) {
    const a = input.slice(); let comparisons = 0, swaps = 0;
    const frames = [{values:a.slice(), active:[], sorted:1, comparisons, swaps, note:'Start with the first value as the sorted section.'}];
    for (let i = 1; i < a.length; i++) {
      let j = i;
      while (j > 0) {
        comparisons++;
        frames.push({values:a.slice(), active:[j-1,j], sorted:i, comparisons, swaps, note:`Compare ${a[j-1]} and ${a[j]}. ${a[j-1]>a[j] ? 'The smaller value belongs to the left.' : 'These values are already in order.'}`});
        if (a[j-1] <= a[j]) break;
        [a[j-1], a[j]] = [a[j], a[j-1]]; swaps++;
        frames.push({values:a.slice(), active:[j-1,j], sorted:i, comparisons, swaps, note:`Swap the pair. Continue moving ${a[j-1]} into position.`});
        j--;
      }
      frames.push({values:a.slice(), active:[], sorted:i+1, comparisons, swaps, note:`The first ${i+1} values are now in order.`});
    }
    frames.push({values:a.slice(), active:[], sorted:a.length, comparisons, swaps, done:true, note:`Sorted. ${comparisons} comparisons and ${swaps} swaps brought the values into ascending order.`});
    return frames;
  }
  function shuffle(values, random = Math.random) {
    const a=values.slice();
    for(let i=a.length-1;i>0;i--){const j=Math.floor(random()*(i+1)); [a[i],a[j]]=[a[j],a[i]];}
    return a;
  }
  return {matches, sortFrames, shuffle};
});
