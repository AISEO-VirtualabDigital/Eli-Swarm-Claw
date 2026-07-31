import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Check, Zap, ArrowRight, Star } from 'lucide-react'
import { useAuthStore } from '../context/authStore'
import toast from 'react-hot-toast'

const plans = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    period: 'forever',
    description: 'Perfect for trying out EliClaw',
    features: [
      '3 SEO audits per month',
      '1 competitor analysis',
      '1 website tracking',
      'Basic website analyzer',
      '1 Swarm Agent',
      '5 content analyses',
      'Community support'
    ],
    cta: 'Get Started',
    popular: false
  },
  {
    id: 'starter',
    name: 'Starter',
    price: 29,
    period: 'month',
    description: 'For freelancers and small teams',
    features: [
      '50 SEO audits per month',
      '5 competitor analyses',
      '3 website tracking',
      'Full automation workflows',
      '3 Swarm Agents',
      '100 content analyses',
      'PDF reports',
      'API access',
      'Email support'
    ],
    cta: 'Start Free Trial',
    popular: true
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 79,
    period: 'month',
    description: 'For growing agencies',
    features: [
      '200 SEO audits per month',
      '15 competitor analyses',
      '10 website tracking',
      'Advanced automation',
      '10 Swarm Agents',
      '500 content analyses',
      'White-label reports',
      'Full API access',
      'Priority support',
      'Team collaboration'
    ],
    cta: 'Start Free Trial',
    popular: false
  },
  {
    id: 'agency',
    name: 'Agency',
    price: 199,
    period: 'month',
    description: 'For large agencies and enterprises',
    features: [
      'Unlimited SEO audits',
      'Unlimited competitors',
      'Unlimited websites',
      'Custom automation',
      'Unlimited Swarm Agents',
      'Unlimited content analysis',
      'White-label everything',
      'Full API + Webhooks',
      'Dedicated support',
      '10 sub-accounts',
      'SSO integration'
    ],
    cta: 'Contact Sales',
    popular: false
  }
]

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState('monthly')
  const { user, token } = useAuthStore()

  const handleSubscribe = async (planId) => {
    if (!user) {
      toast.error('Please sign in first')
      return
    }

    if (planId === 'free') {
      toast.success('You are already on the Free plan!')
      return
    }

    try {
      const res = await fetch('/api/stripe/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          planId,
          successUrl: `${window.location.origin}/dashboard?upgrade=success`,
          cancelUrl: `${window.location.origin}/pricing?canceled=true`
        })
      })

      const data = await res.json()
      if (data.url) {
        window.location.href = data.url
      }
    } catch (err) {
      toast.error('Failed to start checkout')
    }
  }

  return (
    <div className="min-h-screen bg-dark-900 pt-20 pb-20 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h1 className="text-4xl md:text-5xl font-bold mb-4">Simple, Transparent Pricing</h1>
            <p className="text-dark-400 text-lg max-w-2xl mx-auto">
              Start free, upgrade when you need more power. No hidden fees.
            </p>
          </motion.div>

          {/* Billing Toggle */}
          <div className="inline-flex items-center gap-4 mt-8 p-1 bg-dark-800 rounded-xl">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-6 py-2 rounded-lg text-sm font-medium transition-all ${
                billingCycle === 'monthly' ? 'bg-primary-600 text-white' : 'text-dark-400'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('yearly')}
              className={`px-6 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                billingCycle === 'yearly' ? 'bg-primary-600 text-white' : 'text-dark-400'
              }`}
            >
              Yearly
              <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">Save 20%</span>
            </button>
          </div>
        </div>

        {/* Plans */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className={`glass-panel p-6 relative ${plan.popular ? 'border-primary-500/50 ring-2 ring-primary-500/20' : ''}`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="bg-gradient-to-r from-primary-500 to-cyan-400 text-white text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1">
                    <Star size={12} fill="currentColor" /> Most Popular
                  </span>
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-xl font-bold mb-1">{plan.name}</h3>
                <p className="text-sm text-dark-400">{plan.description}</p>
              </div>

              <div className="mb-6">
                <span className="text-4xl font-bold">${billingCycle === 'yearly' ? Math.round(plan.price * 0.8) : plan.price}</span>
                <span className="text-dark-400">/{plan.period}</span>
                {billingCycle === 'yearly' && plan.price > 0 && (
                  <p className="text-sm text-green-400 mt-1">${plan.price * 12 * 0.8}/year (save ${plan.price * 12 * 0.2})</p>
                )}
              </div>

              <button
                onClick={() => handleSubscribe(plan.id)}
                className={`w-full py-3 rounded-xl font-semibold transition-all mb-6 ${
                  plan.popular 
                    ? 'bg-gradient-to-r from-primary-500 to-cyan-400 text-white hover:shadow-lg hover:shadow-primary-500/25' 
                    : 'bg-dark-700 text-white hover:bg-dark-600'
                }`}
              >
                {plan.cta}
              </button>

              <ul className="space-y-3">
                {plan.features.map((feature, j) => (
                  <li key={j} className="flex items-start gap-2 text-sm">
                    <Check size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
                    <span className="text-dark-300">{feature}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* FAQ */}
        <div className="mt-20 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">Frequently Asked Questions</h2>
          <div className="space-y-4">
            {[
              { q: 'Can I change plans anytime?', a: 'Yes, you can upgrade or downgrade at any time. Changes take effect immediately.' },
              { q: 'What happens when I hit my limits?', a: 'You will be notified and can upgrade instantly. No service interruption.' },
              { q: 'Is there a free trial for paid plans?', a: 'Yes, all paid plans include a 14-day free trial. No credit card required.' },
              { q: 'Can I get a refund?', a: 'We offer a 30-day money-back guarantee on all paid plans.' },
            ].map((faq, i) => (
              <div key={i} className="glass-panel p-5">
                <h3 className="font-semibold mb-2">{faq.q}</h3>
                <p className="text-dark-400 text-sm">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}