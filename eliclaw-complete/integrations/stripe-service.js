/**
 * EliClaw Stripe Payment Integration
 * Plans: Free, Starter ($29/mo), Pro ($79/mo), Agency ($199/mo)
 */

const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

const PLANS = {
  free: {
    id: 'free',
    name: 'Free',
    price: 0,
    features: {
      audits: 3,
      competitors: 1,
      websites: 1,
      automation: false,
      swarmAgents: 1,
      contentAnalysis: 5,
      reports: false,
      apiAccess: false,
      whiteLabel: false
    }
  },
  starter: {
    id: 'starter',
    name: 'Starter',
    price: 2900, // $29.00 in cents
    stripePriceId: process.env.STRIPE_STARTER_PRICE_ID,
    features: {
      audits: 50,
      competitors: 5,
      websites: 3,
      automation: true,
      swarmAgents: 3,
      contentAnalysis: 100,
      reports: true,
      apiAccess: true,
      whiteLabel: false
    }
  },
  pro: {
    id: 'pro',
    name: 'Pro',
    price: 7900, // $79.00 in cents
    stripePriceId: process.env.STRIPE_PRO_PRICE_ID,
    features: {
      audits: 200,
      competitors: 15,
      websites: 10,
      automation: true,
      swarmAgents: 10,
      contentAnalysis: 500,
      reports: true,
      apiAccess: true,
      whiteLabel: true
    }
  },
  agency: {
    id: 'agency',
    name: 'Agency',
    price: 19900, // $199.00 in cents
    stripePriceId: process.env.STRIPE_AGENCY_PRICE_ID,
    features: {
      audits: -1, // unlimited
      competitors: -1,
      websites: -1,
      automation: true,
      swarmAgents: -1,
      contentAnalysis: -1,
      reports: true,
      apiAccess: true,
      whiteLabel: true,
      subAccounts: 10,
      prioritySupport: true
    }
  }
};

class PaymentService {
  constructor() {
    this.plans = PLANS;
  }

  // Create checkout session
  async createCheckoutSession({ userId, planId, successUrl, cancelUrl }) {
    const plan = this.plans[planId];
    if (!plan || planId === 'free') {
      throw new Error('Invalid plan or free plan does not require payment');
    }

    const session = await stripe.checkout.sessions.create({
      customer_email: undefined, // Will be set from user data
      line_items: [{
        price: plan.stripePriceId,
        quantity: 1
      }],
      mode: 'subscription',
      success_url: successUrl,
      cancel_url: cancelUrl,
      metadata: {
        userId: userId.toString(),
        planId: planId
      },
      subscription_data: {
        metadata: {
          userId: userId.toString(),
          planId: planId
        }
      }
    });

    return {
      sessionId: session.id,
      url: session.url
    };
  }

  // Create customer portal session
  async createPortalSession({ customerId, returnUrl }) {
    const session = await stripe.billingPortal.sessions.create({
      customer: customerId,
      return_url: returnUrl
    });
    return { url: session.url };
  }

  // Handle webhook events
  async handleWebhook(payload, signature) {
    const event = stripe.webhooks.constructEvent(
      payload,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET
    );

    switch (event.type) {
      case 'checkout.session.completed':
        await this.handleCheckoutComplete(event.data.object);
        break;
      case 'invoice.payment_succeeded':
        await this.handlePaymentSuccess(event.data.object);
        break;
      case 'invoice.payment_failed':
        await this.handlePaymentFailed(event.data.object);
        break;
      case 'customer.subscription.deleted':
        await this.handleSubscriptionCancelled(event.data.object);
        break;
      case 'customer.subscription.updated':
        await this.handleSubscriptionUpdated(event.data.object);
        break;
    }

    return { received: true };
  }

  async handleCheckoutComplete(session) {
    const { userId, planId } = session.metadata;

    // Update user in database
    await pool.query(
      'UPDATE users SET plan = $1, stripe_customer_id = $2, stripe_subscription_id = $3, updated_at = NOW() WHERE id = $4',
      [planId, session.customer, session.subscription, userId]
    );

    // Send welcome email for paid plan
    const userResult = await pool.query('SELECT * FROM users WHERE id = $1', [userId]);
    if (userResult.rows.length > 0) {
      const emailService = require('./email-service');
      await emailService.sendEmail({
        to: userResult.rows[0].email,
        subject: `Welcome to EliClaw ${this.plans[planId].name}!`,
        html: this.getUpgradeEmail(this.plans[planId])
      });
    }
  }

  async handlePaymentSuccess(invoice) {
    // Log payment, update billing history
    await pool.query(
      'INSERT INTO payments (user_id, stripe_invoice_id, amount, status, paid_at) VALUES ($1, $2, $3, $4, $5)',
      [invoice.metadata.userId, invoice.id, invoice.amount_paid, 'succeeded', new Date(invoice.status_transitions.paid_at * 1000)]
    );
  }

  async handlePaymentFailed(invoice) {
    // Notify user
    const userResult = await pool.query('SELECT * FROM users WHERE stripe_customer_id = $1', [invoice.customer]);
    if (userResult.rows.length > 0) {
      const emailService = require('./email-service');
      await emailService.sendEmail({
        to: userResult.rows[0].email,
        subject: 'Payment Failed — Please Update Your Billing Info',
        html: this.getPaymentFailedEmail()
      });
    }
  }

  async handleSubscriptionCancelled(subscription) {
    const { userId } = subscription.metadata;
    await pool.query(
      'UPDATE users SET plan = $1, updated_at = NOW() WHERE id = $2',
      ['free', userId]
    );
  }

  async handleSubscriptionUpdated(subscription) {
    const { userId, planId } = subscription.metadata;
    await pool.query(
      'UPDATE users SET plan = $1, updated_at = NOW() WHERE id = $2',
      [planId, userId]
    );
  }

  // Get upgrade email template
  getUpgradeEmail(plan) {
    return `
      <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: #fff; padding: 40px;">
        <h1 style="background: linear-gradient(135deg, #3b82f6, #22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">EliClaw</h1>
        <h2>Welcome to ${plan.name}!</h2>
        <p>Your subscription is now active. Here's what you can do:</p>
        <ul>
          ${Object.entries(plan.features).map(([key, value]) => `<li>${key}: ${value === -1 ? 'Unlimited' : value}</li>`).join('')}
        </ul>
        <a href="https://eliclaw.virtualabdigital.com/dashboard" style="display: inline-block; background: linear-gradient(135deg, #3b82f6, #22d3ee); color: #fff; padding: 14px 28px; border-radius: 8px; text-decoration: none; font-weight: 600;">Go to Dashboard</a>
      </div>
    `;
  }

  getPaymentFailedEmail() {
    return `
      <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: #fff; padding: 40px;">
        <h1 style="color: #ef4444;">Payment Failed</h1>
        <p>We couldn't process your payment. Please update your billing information to avoid service interruption.</p>
        <a href="https://eliclaw.virtualabdigital.com/settings" style="display: inline-block; background: #ef4444; color: #fff; padding: 14px 28px; border-radius: 8px; text-decoration: none; font-weight: 600;">Update Billing</a>
      </div>
    `;
  }

  // Check feature access
  async checkFeatureAccess(userId, feature) {
    const result = await pool.query('SELECT plan FROM users WHERE id = $1', [userId]);
    if (result.rows.length === 0) return false;

    const plan = this.plans[result.rows[0].plan];
    return plan.features[feature] !== false;
  }

  // Get usage limits
  async getUsageLimits(userId) {
    const result = await pool.query('SELECT plan FROM users WHERE id = $1', [userId]);
    if (result.rows.length === 0) return this.plans.free.features;
    return this.plans[result.rows[0].plan].features;
  }
}

module.exports = { PaymentService, PLANS };