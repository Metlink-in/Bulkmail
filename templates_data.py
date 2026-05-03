"""
Global starter email templates — inserted once via POST /admin/seed-templates.
All CSS is inline so templates render correctly in Gmail, Outlook, Apple Mail etc.
Merge tags supported: {name}  {first_name}  {org}  {email}
"""

GLOBAL_TEMPLATES = [
    # ──────────────────────────────────────────────────────────────────────
    # 1. Cold B2B Outreach — Blue gradient
    # ──────────────────────────────────────────────────────────────────────
    {
        "name": "Cold B2B Outreach — Blue",
        "subject": "Quick question for {first_name} at {org}",
        "html_body": """
<div style="max-width:600px;margin:0 auto;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;border-radius:14px;overflow:hidden;border:1px solid #e5e7eb;">

  <!-- HEADER -->
  <div style="background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 100%);padding:44px 40px;text-align:center;">
    <div style="font-size:40px;margin-bottom:14px;">🎯</div>
    <h1 style="color:#ffffff;font-size:26px;font-weight:800;margin:0 0 8px;line-height:1.25;">Hi {first_name} — got a quick minute?</h1>
    <p style="color:rgba(255,255,255,0.75);font-size:14px;margin:0;letter-spacing:0.4px;">A short note that might be worth your time</p>
  </div>

  <!-- BODY -->
  <div style="background:#ffffff;padding:40px;">
    <p style="font-size:16px;color:#111827;line-height:1.8;margin:0 0 18px;">I was researching <strong style="color:#2563eb;">{org}</strong> this week and was genuinely impressed — it's rare to see this level of execution.</p>
    <p style="font-size:16px;color:#374151;line-height:1.8;margin:0 0 28px;">We help B2B teams <strong>increase qualified replies by 40%</strong> in under 60 days through AI-personalized outreach — without burning domain reputation or adding manual work.</p>

    <!-- BENEFITS BOX -->
    <div style="background:#eff6ff;border-radius:10px;padding:24px 28px;margin:0 0 28px;border:1px solid #bfdbfe;">
      <p style="margin:0 0 12px;font-size:15px;font-weight:700;color:#1e40af;">What teams like {org} get:</p>
      <p style="margin:0 0 8px;font-size:14px;color:#374151;line-height:1.6;">✅ &nbsp;Personalized cold email at scale</p>
      <p style="margin:0 0 8px;font-size:14px;color:#374151;line-height:1.6;">✅ &nbsp;Auto reply tracking &amp; inbox sync</p>
      <p style="margin:0;font-size:14px;color:#374151;line-height:1.6;">✅ &nbsp;Deliverability protection built-in</p>
    </div>

    <!-- CTA -->
    <div style="text-align:center;margin:0 0 32px;">
      <a href="#" style="display:inline-block;background:linear-gradient(135deg,#1e3a8a,#2563eb);color:#ffffff;font-size:15px;font-weight:700;padding:15px 42px;border-radius:8px;text-decoration:none;">Book a Free 15-Min Call →</a>
    </div>

    <p style="font-size:14px;color:#6b7280;line-height:1.6;margin:0;font-style:italic;">Happy to share 2–3 specific ideas for {org} even if we don't end up working together. No pressure.</p>
  </div>

  <!-- FOOTER -->
  <div style="background:#f8fafc;padding:22px 40px;border-top:1px solid #e5e7eb;">
    <p style="margin:0;font-size:13px;color:#9ca3af;">Sent via BulkReach Pro &nbsp;·&nbsp; To unsubscribe reply <em>stop</em></p>
  </div>

</div>
"""
    },

    # ──────────────────────────────────────────────────────────────────────
    # 2. Partnership / Collaboration — Purple
    # ──────────────────────────────────────────────────────────────────────
    {
        "name": "Partnership Proposal — Purple",
        "subject": "Collaboration idea for {org} — worth 5 minutes?",
        "html_body": """
<div style="max-width:600px;margin:0 auto;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;border-radius:14px;overflow:hidden;border:1px solid #e5e7eb;">

  <!-- HEADER -->
  <div style="background:linear-gradient(135deg,#4c1d95 0%,#7c3aed 50%,#a855f7 100%);padding:44px 40px;text-align:center;">
    <div style="font-size:40px;margin-bottom:14px;">🤝</div>
    <h1 style="color:#ffffff;font-size:25px;font-weight:800;margin:0 0 8px;line-height:1.3;">{first_name}, I think we can build something great together</h1>
    <p style="color:rgba(255,255,255,0.75);font-size:14px;margin:0;">A mutual-growth opportunity for {org}</p>
  </div>

  <!-- BODY -->
  <div style="background:#ffffff;padding:40px;">
    <p style="font-size:16px;color:#111827;line-height:1.8;margin:0 0 18px;">Hi {first_name},</p>
    <p style="font-size:16px;color:#374151;line-height:1.8;margin:0 0 20px;">I've been following <strong style="color:#7c3aed;">{org}</strong> for a while and I keep coming back to one thought — our audiences overlap significantly, and a strategic collaboration could benefit both sides.</p>

    <!-- IDEA BOXES -->
    <div style="display:table;width:100%;margin:0 0 28px;">
      <div style="display:table-row;">
        <div style="display:table-cell;width:48%;background:#faf5ff;border-radius:10px;padding:20px;border:1px solid #e9d5ff;vertical-align:top;">
          <p style="margin:0 0 8px;font-size:22px;">💡</p>
          <p style="margin:0 0 6px;font-size:14px;font-weight:700;color:#6d28d9;">Co-marketing</p>
          <p style="margin:0;font-size:13px;color:#374151;line-height:1.5;">Joint webinars, content swaps, or newsletter cross-promos</p>
        </div>
        <td style="width:4%;"></td>
        <div style="display:table-cell;width:48%;background:#faf5ff;border-radius:10px;padding:20px;border:1px solid #e9d5ff;vertical-align:top;">
          <p style="margin:0 0 8px;font-size:22px;">🔗</p>
          <p style="margin:0 0 6px;font-size:14px;font-weight:700;color:#6d28d9;">Integration / Referral</p>
          <p style="margin:0;font-size:13px;color:#374151;line-height:1.5;">Warm referrals and a shared revenue model</p>
        </div>
      </div>
    </div>

    <p style="font-size:16px;color:#374151;line-height:1.8;margin:0 0 28px;">I'd love to jump on a 20-minute call to explore what makes sense for both teams — no commitment required.</p>

    <!-- CTA -->
    <div style="text-align:center;margin:0 0 28px;">
      <a href="#" style="display:inline-block;background:linear-gradient(135deg,#4c1d95,#7c3aed);color:#ffffff;font-size:15px;font-weight:700;padding:15px 42px;border-radius:8px;text-decoration:none;">Let's Explore This Together →</a>
    </div>

    <p style="font-size:14px;color:#6b7280;line-height:1.6;margin:0;">Looking forward to hearing your thoughts, {first_name}.</p>
  </div>

  <!-- FOOTER -->
  <div style="background:#faf5ff;padding:22px 40px;border-top:1px solid #e9d5ff;">
    <p style="margin:0;font-size:13px;color:#9ca3af;">Sent via BulkReach Pro &nbsp;·&nbsp; To unsubscribe reply <em>stop</em></p>
  </div>

</div>
"""
    },

    # ──────────────────────────────────────────────────────────────────────
    # 3. SaaS Demo Invite — Teal / Green
    # ──────────────────────────────────────────────────────────────────────
    {
        "name": "SaaS Demo Invite — Teal",
        "subject": "See exactly how {org} could use this, {first_name}",
        "html_body": """
<div style="max-width:600px;margin:0 auto;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;border-radius:14px;overflow:hidden;border:1px solid #e5e7eb;">

  <!-- HEADER -->
  <div style="background:linear-gradient(135deg,#065f46 0%,#059669 60%,#34d399 100%);padding:44px 40px;text-align:center;">
    <div style="font-size:40px;margin-bottom:14px;">⚡</div>
    <h1 style="color:#ffffff;font-size:25px;font-weight:800;margin:0 0 8px;line-height:1.3;">Live demo built around {org}</h1>
    <p style="color:rgba(255,255,255,0.8);font-size:14px;margin:0;">20 minutes · personalised · zero fluff</p>
  </div>

  <!-- BODY -->
  <div style="background:#ffffff;padding:40px;">
    <p style="font-size:16px;color:#111827;line-height:1.8;margin:0 0 18px;">Hi {first_name},</p>
    <p style="font-size:16px;color:#374151;line-height:1.8;margin:0 0 24px;">I'd love to show you a live walkthrough tailored specifically to <strong style="color:#059669;">{org}</strong> — not a generic product tour, but a session built around your actual workflow and goals.</p>

    <!-- AGENDA -->
    <div style="background:#ecfdf5;border-radius:10px;padding:24px 28px;margin:0 0 28px;border:1px solid #a7f3d0;">
      <p style="margin:0 0 14px;font-size:15px;font-weight:700;color:#065f46;">What we'll cover in 20 min:</p>
      <div style="display:flex;align-items:flex-start;margin-bottom:12px;">
        <span style="background:#059669;color:#fff;border-radius:50%;width:22px;height:22px;display:inline-block;text-align:center;font-size:12px;font-weight:700;line-height:22px;margin-right:12px;flex-shrink:0;">1</span>
        <p style="margin:0;font-size:14px;color:#374151;line-height:1.5;">Your current outreach bottlenecks — honest diagnosis</p>
      </div>
      <div style="display:flex;align-items:flex-start;margin-bottom:12px;">
        <span style="background:#059669;color:#fff;border-radius:50%;width:22px;height:22px;display:inline-block;text-align:center;font-size:12px;font-weight:700;line-height:22px;margin-right:12px;flex-shrink:0;">2</span>
        <p style="margin:0;font-size:14px;color:#374151;line-height:1.5;">Live demo with your prospect data &amp; templates</p>
      </div>
      <div style="display:flex;align-items:flex-start;">
        <span style="background:#059669;color:#fff;border-radius:50%;width:22px;height:22px;display:inline-block;text-align:center;font-size:12px;font-weight:700;line-height:22px;margin-right:12px;flex-shrink:0;">3</span>
        <p style="margin:0;font-size:14px;color:#374151;line-height:1.5;">ROI estimate specific to {org}'s team size</p>
      </div>
    </div>

    <!-- CTA -->
    <div style="text-align:center;margin:0 0 28px;">
      <a href="#" style="display:inline-block;background:linear-gradient(135deg,#065f46,#059669);color:#ffffff;font-size:15px;font-weight:700;padding:15px 42px;border-radius:8px;text-decoration:none;">Pick a Time That Works →</a>
    </div>

    <p style="font-size:14px;color:#6b7280;line-height:1.6;margin:0;">Spots fill fast — I keep it to 3 demos per week so I can give each one full attention.</p>
  </div>

  <!-- FOOTER -->
  <div style="background:#ecfdf5;padding:22px 40px;border-top:1px solid #a7f3d0;">
    <p style="margin:0;font-size:13px;color:#9ca3af;">Sent via BulkReach Pro &nbsp;·&nbsp; To unsubscribe reply <em>stop</em></p>
  </div>

</div>
"""
    },

    # ──────────────────────────────────────────────────────────────────────
    # 4. Follow-Up Email — Warm Orange / Amber
    # ──────────────────────────────────────────────────────────────────────
    {
        "name": "Follow-Up — Warm Orange",
        "subject": "Did my last email get buried, {first_name}?",
        "html_body": """
<div style="max-width:600px;margin:0 auto;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;border-radius:14px;overflow:hidden;border:1px solid #e5e7eb;">

  <!-- HEADER -->
  <div style="background:linear-gradient(135deg,#92400e 0%,#d97706 60%,#fbbf24 100%);padding:40px;text-align:center;">
    <div style="font-size:40px;margin-bottom:14px;">📬</div>
    <h1 style="color:#ffffff;font-size:24px;font-weight:800;margin:0 0 6px;line-height:1.3;">Just checking in, {first_name}</h1>
    <p style="color:rgba(255,255,255,0.8);font-size:14px;margin:0;">I know inboxes get crazy — no worries at all</p>
  </div>

  <!-- BODY -->
  <div style="background:#ffffff;padding:40px;">
    <p style="font-size:16px;color:#111827;line-height:1.8;margin:0 0 18px;">Hi {first_name},</p>
    <p style="font-size:16px;color:#374151;line-height:1.8;margin:0 0 20px;">I reached out last week about helping <strong style="color:#d97706;">{org}</strong> with outreach. I know how fast things move, so I wanted to bump this up in case it got buried.</p>

    <!-- REMINDER CARD -->
    <div style="background:#fffbeb;border-radius:10px;padding:24px 28px;margin:0 0 28px;border-left:4px solid #f59e0b;">
      <p style="margin:0 0 8px;font-size:15px;font-weight:700;color:#92400e;">The short version:</p>
      <p style="margin:0;font-size:14px;color:#374151;line-height:1.7;">We help teams like {org} send smarter outreach emails — personalized at scale, with built-in reply tracking and deliverability protection. Most teams see results in the first 2 weeks.</p>
    </div>

    <p style="font-size:16px;color:#374151;line-height:1.8;margin:0 0 8px;">Three quick options:</p>
    <p style="font-size:14px;color:#374151;line-height:1.6;margin:0 0 6px;">👉 &nbsp;<strong>Interested</strong> — reply and I'll send over a time to chat</p>
    <p style="font-size:14px;color:#374151;line-height:1.6;margin:0 0 6px;">👉 &nbsp;<strong>Not now</strong> — totally fine, I'll follow up in a month</p>
    <p style="font-size:14px;color:#374151;line-height:1.6;margin:0 0 28px;">👉 &nbsp;<strong>Not a fit</strong> — just say so and I'll stop reaching out, no hard feelings</p>

    <!-- CTA -->
    <div style="text-align:center;margin:0 0 24px;">
      <a href="#" style="display:inline-block;background:linear-gradient(135deg,#92400e,#d97706);color:#ffffff;font-size:15px;font-weight:700;padding:14px 40px;border-radius:8px;text-decoration:none;">Yes, Let's Talk →</a>
    </div>

    <p style="font-size:14px;color:#6b7280;line-height:1.6;margin:0;">Either way, I appreciate your time {first_name}. Have a great rest of your week!</p>
  </div>

  <!-- FOOTER -->
  <div style="background:#fffbeb;padding:22px 40px;border-top:1px solid #fde68a;">
    <p style="margin:0;font-size:13px;color:#9ca3af;">Sent via BulkReach Pro &nbsp;·&nbsp; To unsubscribe reply <em>stop</em></p>
  </div>

</div>
"""
    },

    # ──────────────────────────────────────────────────────────────────────
    # 5. Executive Introduction — Dark Navy / Professional
    # ──────────────────────────────────────────────────────────────────────
    {
        "name": "Executive Introduction — Dark Navy",
        "subject": "{first_name}, a brief thought on {org}'s growth",
        "html_body": """
<div style="max-width:600px;margin:0 auto;font-family:Georgia,'Times New Roman',serif;border-radius:14px;overflow:hidden;border:1px solid #e5e7eb;">

  <!-- HEADER -->
  <div style="background:linear-gradient(135deg,#0f172a 0%,#1e293b 60%,#334155 100%);padding:44px 40px;">
    <p style="margin:0 0 20px;font-size:11px;font-weight:700;letter-spacing:2px;color:#94a3b8;text-transform:uppercase;">Confidential &nbsp;·&nbsp; For {first_name} only</p>
    <h1 style="color:#f8fafc;font-size:26px;font-weight:700;margin:0 0 12px;line-height:1.35;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;">{first_name},</h1>
    <p style="color:#cbd5e1;font-size:16px;margin:0;line-height:1.6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;">I'll keep this brief — your time is valuable.</p>
    <div style="width:50px;height:3px;background:linear-gradient(90deg,#3b82f6,#8b5cf6);margin-top:24px;border-radius:2px;"></div>
  </div>

  <!-- BODY -->
  <div style="background:#ffffff;padding:40px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;">
    <p style="font-size:16px;color:#1e293b;line-height:1.85;margin:0 0 20px;">I've studied <strong>{org}</strong>'s market position and I believe you're sitting on an untapped growth lever that most of your competitors haven't figured out yet: <em>systematic, relationship-first outreach at scale</em>.</p>

    <p style="font-size:16px;color:#374151;line-height:1.85;margin:0 0 28px;">The companies winning right now aren't sending more emails — they're sending <strong>smarter ones</strong>. Personalized, timed, and tracked with precision. We built the infrastructure for exactly that.</p>

    <!-- STATS ROW -->
    <div style="display:table;width:100%;margin:0 0 32px;border-collapse:separate;border-spacing:0;">
      <div style="display:table-row;">
        <div style="display:table-cell;width:31%;background:#f8fafc;border-radius:10px;padding:20px;text-align:center;border:1px solid #e2e8f0;">
          <p style="margin:0 0 4px;font-size:28px;font-weight:800;color:#1e3a8a;">3×</p>
          <p style="margin:0;font-size:12px;color:#64748b;line-height:1.4;">Average reply rate increase</p>
        </div>
        <td style="width:3%;"></td>
        <div style="display:table-cell;width:31%;background:#f8fafc;border-radius:10px;padding:20px;text-align:center;border:1px solid #e2e8f0;">
          <p style="margin:0 0 4px;font-size:28px;font-weight:800;color:#1e3a8a;">60d</p>
          <p style="margin:0;font-size:12px;color:#64748b;line-height:1.4;">To measurable pipeline growth</p>
        </div>
        <td style="width:3%;"></td>
        <div style="display:table-cell;width:31%;background:#f8fafc;border-radius:10px;padding:20px;text-align:center;border:1px solid #e2e8f0;">
          <p style="margin:0 0 4px;font-size:28px;font-weight:800;color:#1e3a8a;">0</p>
          <p style="margin:0;font-size:12px;color:#64748b;line-height:1.4;">Spam filters triggered</p>
        </div>
      </div>
    </div>

    <p style="font-size:15px;color:#374151;line-height:1.8;margin:0 0 28px;">I'd welcome a 20-minute call at your convenience, {first_name}. No deck, no pitch script — just a direct conversation about whether this makes sense for {org}.</p>

    <!-- CTA -->
    <div style="text-align:center;margin:0 0 28px;">
      <a href="#" style="display:inline-block;background:linear-gradient(135deg,#0f172a,#1e40af);color:#ffffff;font-size:14px;font-weight:700;padding:15px 44px;border-radius:8px;text-decoration:none;letter-spacing:0.5px;">Request a Private Briefing →</a>
    </div>

    <p style="font-size:13px;color:#94a3b8;line-height:1.6;margin:0;border-top:1px solid #f1f5f9;padding-top:20px;">If this isn't relevant for {org} right now, I understand completely. Simply reply and I'll remove you from my list.</p>
  </div>

  <!-- FOOTER -->
  <div style="background:#0f172a;padding:22px 40px;">
    <p style="margin:0;font-size:12px;color:#475569;letter-spacing:0.5px;">BULKREACH PRO &nbsp;·&nbsp; To unsubscribe reply <em style="color:#64748b;">stop</em></p>
  </div>

</div>
"""
    },

    # ──────────────────────────────────────────────────────────────────────
    # Metlink Outreach — Purple gradient
    # ──────────────────────────────────────────────────────────────────────
    {
        "name": "Metlink Outreach",
        "subject": "Quick question for {first_name} at {org}",
        "html_body": """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Metlink Outreach</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f7fb; font-family:Arial, sans-serif;">

  <table align="center" width="600" cellpadding="0" cellspacing="0"
         style="background:#ffffff; border-radius:10px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.08);">

    <!-- Header -->
    <tr>
      <td style="background:linear-gradient(90deg, #4A00E0, #8E2DE2); padding:25px; text-align:center; color:white;">
        <h1 style="margin:0; font-size:26px;">Metlink</h1>
        <p style="margin:5px 0 0; font-size:14px;">Smart Solutions. Real Growth.</p>
      </td>
    </tr>

    <!-- Body -->
    <tr>
      <td style="padding:30px; color:#333;">

        <h2 style="margin-top:0; color:#4A00E0;">Let's Help You Scale Faster 🚀</h2>

        <p style="font-size:15px; line-height:1.6;">Hi <strong>{first_name}</strong>,</p>

        <p style="font-size:15px; line-height:1.6;">
          I came across your work at <strong>{org}</strong> and noticed how you're building in your space.
        </p>

        <p style="font-size:15px; line-height:1.6;">
          At <strong>Metlink</strong>, we help businesses like yours streamline operations, automate workflows,
          and unlock scalable growth using modern tech and AI-driven systems.
        </p>

        <!-- Highlight Box -->
        <div style="background:#f1efff; padding:15px; border-radius:8px; margin:20px 0;">
          <p style="margin:0; font-size:14px;">
            ⚡ <strong>What we can help with:</strong><br>
            &bull; Automation &amp; AI integration<br>
            &bull; Custom web &amp; backend systems<br>
            &bull; Growth-focused digital solutions
          </p>
        </div>

        <p style="font-size:15px; line-height:1.6;">
          Would you be open to a quick 15-minute chat to explore if this aligns with your current goals?
        </p>

        <!-- CTA Button -->
        <div style="text-align:center; margin:30px 0;">
          <a href="#" style="background:#4A00E0; color:#fff; text-decoration:none; padding:12px 25px; border-radius:6px; font-size:15px; display:inline-block;">
            Book a Quick Call
          </a>
        </div>

        <p style="font-size:14px; color:#777;">
          Looking forward to connecting.<br><br>
          <strong>Metlink Team</strong>
        </p>

      </td>
    </tr>

    <!-- Footer -->
    <tr>
      <td style="background:#f4f7fb; padding:15px; text-align:center; font-size:12px; color:#888;">
        &copy; 2026 Metlink | All rights reserved<br>
        <a href="#" style="color:#8E2DE2; text-decoration:none;">Unsubscribe</a>
      </td>
    </tr>

  </table>

</body>
</html>""",
    },
]
