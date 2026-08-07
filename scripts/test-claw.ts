// Integration test: Open Claw + Omni Route
import { getOpenClaw } from '../src/lib/open-claw';
import { OmniRoute } from '../src/lib/omni-route';

async function main() {
  console.log('=== OPEN CLAW STANDALONE TEST ===\n');

  const claw = getOpenClaw();

  // 1. Generate from Guerrilla Mail
  console.log('1. Spawning Guerrilla Mail inbox...');
  const gm = await claw.generate('guerrilla');
  console.log(`   Email: ${gm.email}`);
  console.log(`   Provider: ${gm.provider}`);
  console.log(`   TTL: ${Math.round((gm.expiresAt - Date.now()) / 60000)}min`);

  // 2. Generate from mail.tm
  console.log('\n2. Spawning mail.tm inbox...');
  const mt = await claw.generate('mailtm');
  console.log(`   Email: ${mt.email}`);
  console.log(`   Provider: ${mt.provider}`);
  console.log(`   TTL: ${Math.round((mt.expiresAt - Date.now()) / 60000)}min`);

  // 3. Generate from OpenInbox
  console.log('\n3. Spawning OpenInbox inbox...');
  const oi = await claw.generate('openinbox');
  console.log(`   Email: ${oi.email}`);
  console.log(`   Provider: ${oi.provider}`);
  console.log(`   TTL: ${Math.round((oi.expiresAt - Date.now()) / 60000)}min`);

  // 4. Check all inboxes for emails
  console.log('\n4. Checking all inboxes...');
  const results = await claw.pollAll();
  console.log(`   Inboxes with mail: ${results.size}`);

  // 5. Get state
  console.log('\n5. Claw state:');
  const state = claw.getState();
  console.log(`   Total generated: ${state.totalGenerated}`);
  console.log(`   Total emails read: ${state.totalEmailsRead}`);
  console.log(`   Provider stats:`, JSON.stringify(state.providerStats, null, 2));

  claw.stopPolling();

  // ─── OMNI ROUTE TEST ───
  console.log('\n=== OMNI ROUTE + CLAW TEST ===\n');

  const omni = new OmniRoute({ preRotateMinutes: 5 });

  // 6. Check state with the injected Gemini key
  console.log('6. Omni state (with AQ. key from env):');
  const omniState = omni.getState();
  console.log(`   Mode: ${omniState.mode}`);
  console.log(`   Has valid key: ${omni.hasValidKey()}`);
  console.log(`   Active key: ${omniState.activeKey ? omniState.activeKey.key.slice(0, 12) + '...' : 'none'}`);

  // 7. Force rotation (claw spawns new inbox)
  console.log('\n7. Force rotation via claw...');
  const newKey = await omni.rotate('gemini');
  if (newKey) {
    console.log(`   New inbox: ${newKey.inboxEmail}`);
    console.log(`   Provider: ${newKey.provider}`);
    console.log(`   Status: ${newKey.status}`);
  }

  // 8. Get signup instructions
  console.log('\n8. Signup instructions:');
  const instructions = await omni.getSignupInstructions('gemini');
  if (instructions) {
    console.log(`   Email: ${instructions.email}`);
    console.log(`   URL: ${instructions.url}`);
    console.log(`   Provider: ${instructions.provider}`);
  }

  // 9. Test manual injection
  console.log('\n9. Manual injection test...');
  const injected = omni.injectKey('gemini', 'AIzaSyTestKey123456789abcdefghijklmnopqrstu', 'test');
  console.log(`   Key: ${injected.key.slice(0, 12)}...`);
  console.log(`   Source: ${injected.inboxEmail}`);

  omni.stopAutoRotation();

  console.log('\n✓ All tests passed');
}

main().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
