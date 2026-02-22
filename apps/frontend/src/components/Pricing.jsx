import React from "react";
import "./Pricing.css";

export default function Pricing() {
  return (
    <div className="pricing-page">
      <div className="container">
        <div className="header">
          <h1>🚀 CloudGuardian</h1>
          <h2>Planos de Segurança DevSecOps</h2>
          <p>Proteção enterprise para sua infraestrutura cloud</p>
        </div>

        <div className="cards">
          <div className="card">
            <h3>Starter</h3>
            <div className="price">R$ 299<span>/mês</span></div>
            <ul>
              <li>✅ Até 5 projetos</li>
              <li>✅ 10.000 scans/mês</li>
              <li>✅ Compliance SOC2</li>
              <li>✅ Secret Scanning</li>
              <li>❌ Drift Detection</li>
            </ul>
            <button>Começar Agora</button>
          </div>

          <div className="card popular">
            <div className="badge">MAIS POPULAR</div>
            <h3>Pro</h3>
            <div className="price">R$ 899<span>/mês</span></div>
            <ul>
              <li>✅ Até 50 projetos</li>
              <li>✅ 100.000 scans/mês</li>
              <li>✅ Todos frameworks compliance</li>
              <li>✅ Secret Scanning avançado</li>
              <li>✅ Drift Detection</li>
            </ul>
            <button className="primary">Testar 14 Dias Grátis</button>
          </div>

          <div className="card">
            <h3>Enterprise</h3>
            <div className="price">R$ 2.999<span>/mês</span></div>
            <ul>
              <li>✅ Projetos ilimitados</li>
              <li>✅ Scans ilimitados</li>
              <li>✅ Todos frameworks</li>
              <li>✅ Auto-remediação</li>
              <li>✅ Suporte 24/7</li>
            </ul>
            <button>Falar com Vendas</button>
          </div>
        </div>

        <div className="footer">
          <h3>💼 Precisa de algo personalizado?</h3>
          <p>Entre em contato para uma demonstração customizada</p>
          <button className="contact">Agendar Demonstração</button>
        </div>
      </div>
    </div>
  );
}
