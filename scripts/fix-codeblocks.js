const fs = require('fs');
let c = fs.readFileSync('generate-safety-guide.js', 'utf8');

// Only fix codeBlocks that still use backtick template literals
// (the ones already using string concat are fine)
c = c.replace(/codeBlock\(`([\s\S]*?)`\)/gs, (match, inner) => {
  let fixed = inner.replace(/'/g, "\\'");
  return "codeBlock('" + fixed + "')";
});

fs.writeFileSync('generate-safety-guide.js', c);
console.log('Done');
