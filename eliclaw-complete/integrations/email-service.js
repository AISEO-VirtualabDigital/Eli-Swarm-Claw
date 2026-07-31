/**
 * EliClaw Email Automation Service
 * Supports: SendGrid, Resend, SMTP fallback
 */

const axios = require('axios');
const nodemailer = require('nodemailer');

class EmailService {
  constructor() {
    this.provider = process.env.EMAIL_PROVIDER || 'resend'; // sendgrid, resend, smtp
    this.fromEmail = process.env.FROM_EMAIL || 'noreply@eliclaw.virtualabdigital.com';
    this.fromName = process.env.FROM_NAME || 'EliClaw by Virtualab Digital';

    // Initialize provider
    switch(this.provider) {
      case 'sendgrid':
        this.sgApiKey = process.env.SENDGRID_API_KEY;
        break;
      case 'resend':
        this.resendApiKey = process.env.RESEND_API_KEY;
        break;
      case 'smtp':
        this.transporter = nodemailer.createTransporter({
          host: process.env.SMTP_HOST,
          port: process.env.SMTP_PORT || 587,
          secure: process.env.SMTP_SECURE === 'true',
          auth: {
            user: process.env.SMTP_USER,
            pass: process.env.SMTP_PASS
          }
        });
        break;
    }
  }

  async sendEmail({ to, subject, html, text, attachments = [] }) {
    try {
      switch(this.provider) {
        case 'sendgrid':
          return await this.sendViaSendGrid({ to, subject, html, text, attachments });
        case 'resend':
          return await this.sendViaResend({ to, subject, html, text, attachments });
        case 'smtp':
          return await this.sendViaSMTP({ to, subject, html, text, attachments });
        default:
          throw new Error('Unknown email provider');
      }
    } catch (err) {
      console.error('Email send error:', err);
      throw err;
    }
  }

  async sendViaSendGrid({ to, subject, html, text }) {
    const response = await axios.post('https://api.sendgrid.com/v3/mail/send', {
      personalizations: [{ to: [{ email: to }] }],
      from: { email: this.fromEmail, name: this.fromName },
      subject,
      content: [
        { type: 'text/plain', value: text || '' },
        { type: 'text/html', value: html }
      ]
    }, {
      headers: { 'Authorization': `Bearer ${this.sgApiKey}` }
    });
    return { success: true, provider: 'sendgrid', messageId: response.headers['x-message-id'] };
  }

  async sendViaResend({ to, subject, html, text }) {
    const response = await axios.post('https://api.resend.com/emails', {
      from: `${this.fromName} <${this.fromEmail}>`,
      to,
      subject,
      html,
      text
    }, {
      headers: { 'Authorization': `Bearer ${this.resendApiKey}` }
    });
    return { success: true, provider: 'resend', messageId: response.data.id };
  }

  async sendViaSMTP({ to, subject, html, text, attachments }) {
    const info = await this.transporter.sendMail({
      from: `"${this.fromName}" <${this.fromEmail}>`,
      to,
      subject,
      text,
      html,
      attachments
    });
    return { success: true, provider: 'smtp', messageId: info.messageId };
  }

  // ===== EMAIL SEQUENCES =====

  async sendWelcomeEmail(user) {
    const html = this.getTemplate('welcome', { name: user.name, dashboardUrl: 'https://eliclaw.virtualabdigital.com/dashboard' });
    return this.sendEmail({
      to: user.email,
      subject: 'Welcome to EliClaw — Your Growth Journey Starts Now',
      html
    });
  }

  async sendAuditReport(email, auditData) {
    const html = this.getTemplate('audit-report', auditData);
    return this.sendEmail({
      to: email,
      subject: `Your SEO Audit Report for ${auditData.url}`,
      html
    });
  }

  async sendLeadNotification(lead) {
    const adminEmail = process.env.ADMIN_EMAIL || 'admin@virtualabdigital.com';
    const html = this.getTemplate('lead-notification', lead);
    return this.sendEmail({
      to: adminEmail,
      subject: `New Lead: ${lead.name} from ${lead.source}`,
      html
    });
  }

  async sendWeeklyReport(user, stats) {
    const html = this.getTemplate('weekly-report', { ...stats, name: user.name });
    return this.sendEmail({
      to: user.email,
      subject: 'Your Weekly EliClaw Growth Report',
      html
    });
  }

  async sendCompetitorAlert(user, competitor, changes) {
    const html = this.getTemplate('competitor-alert', { competitor, changes });
    return this.sendEmail({
      to: user.email,
      subject: `Alert: ${competitor} Made Significant Changes`,
      html
    });
  }

  // ===== TEMPLATE ENGINE =====

  getTemplate(name, data) {
    const templates = {
      welcome: require('../email-templates/welcome'),
      'audit-report': require('../email-templates/audit-report'),
      'lead-notification': require('../email-templates/lead-notification'),
      'weekly-report': require('../email-templates/weekly-report'),
      'competitor-alert': require('../email-templates/competitor-alert')
    };
    return templates[name](data);
  }
}

module.exports = EmailService;