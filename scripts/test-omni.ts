import { OmniRoute } from '../src/lib/omni-route';

async function test() {
  const omni = new OmniRoute({
    preRotateMinutes: 10,
  });
  
  console.log('=== Test 1: Create Inbox ===');
  const inbox = await omni.createInbox('eli-test-1');
  console.log('Inbox:', inbox);
  console.log('Pool size:', omni.getState().inboxPool.length);
  
  console.log('\n=== Test 2: Force Rotation ===');
  const rotation = await omni.rotate('gemini');
  console.log('Rotation:', {
    service: rotation?.service,
    status: rotation?.status,
    inboxEmail: rotation?.inboxEmail,
    keyExtracted: !!rotation?.key,
  });
  
  console.log('\n=== Test 3: State ===');
  const state = omni.getState();
  console.log('Active key:', state.activeKey ? 'YES' : 'NO');
  console.log('Total rotations:', state.totalRotations);
  console.log('Inbox pool:', state.inboxPool.length);
  
  console.log('\n=== Test 4: Inject Manual Key ===');
  const injected = omni.injectKey('gemini', 'AIzaSyTestKey123456789012345678901234');
  console.log('Injected:', injected.key.slice(0, 8) + '...');
  console.log('Active key now:', omni.getActiveKey().slice(0, 8) + '...');
  
  omni.stopAutoRotation();
  console.log('\nAll tests passed!');
}

test().catch(e => { console.error('TEST FAILED:', e); process.exit(1); });
