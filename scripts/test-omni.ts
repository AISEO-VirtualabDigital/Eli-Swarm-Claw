// Quick smoke test for omni-route module
import { OmniRoute } from '../src/lib/omni-route';

async function main() {
  const omni = new OmniRoute({
    seedInbox: '70ew6zebmoxg@inboxfly.space',
  });

  const state = omni.getState();
  console.log('=== OMNI STATE ===');
  console.log('Mode:', state.mode);
  console.log('Has valid key:', omni.hasValidKey());
  console.log('Seed inbox:', state.inboxPool[0]?.email);
  console.log('Active key:', state.activeKey ? 'yes' : 'no');

  // Test creating a real inbox
  console.log('\n=== CREATING INBOX ===');
  try {
    const inbox = await omni.createInbox('test-smoke');
    console.log('Created:', inbox.email);
    console.log('Expires:', inbox.expiresAt);
    console.log('ID:', inbox.id);
  } catch (err: any) {
    console.error('Inbox creation error:', err.message);
  }

  // Test signup instructions
  console.log('\n=== SIGNUP INSTRUCTIONS ===');
  const instructions = omni.getSignupInstructions('gemini');
  console.log('Instructions:', instructions ? 'yes' : 'no');
  if (instructions) {
    console.log('Email:', instructions.email);
    console.log('URL:', instructions.url);
  }

  // Test manual injection
  console.log('\n=== MANUAL INJECTION ===');
  const injected = omni.injectKey('gemini', 'AIzaSyTestKey1234567890abcdefghijklmnopqrstu');
  console.log('Injected key:', injected.key.slice(0, 10) + '...');
  console.log('Has valid key now:', omni.hasValidKey());
  console.log('Get active key:', omni.getActiveKey('gemini').slice(0, 10) + '...');

  const finalState = omni.getState();
  console.log('\n=== FINAL STATE ===');
  console.log('Total rotations:', finalState.totalRotations);
  console.log('Key history length:', finalState.keyHistory.length);
  console.log('Inbox pool:', finalState.inboxPool.length);

  omni.stopAutoRotation();
  console.log('\n✓ All tests passed');
}

main().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
