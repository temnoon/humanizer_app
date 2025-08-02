# Chapter 3: Noether Theorem and Dirac

<!-- LATEX_PROTECTION_START -->
<!-- This content contains protected LaTeX expressions -->
<!-- Enhanced LaTeX Plugin will process data-latex attributes -->


*Conversation from December 05, 2024*

## Message 1

Give me an article explaining the proof of Noether's theorem (not necessarily displaying the entire proof) and applying it to the example of the Dirac equation.

---

## Message 2

**Title: Noether’s Theorem and Its Application to the Dirac Equation**

**Abstract:**  
Noether’s theorem is a cornerstone of modern theoretical physics, forging a profound connection between the symmetries of a physical system and its conservation laws. In essence, it states that for every continuous symmetry of the action of a physical system, there is a corresponding conserved current and an associated conserved quantity. This result is foundational in classical and quantum field theories, providing a unifying framework for understanding why certain quantities remain invariant under time evolution. In this article, we first outline the conceptual setting and main steps of Noether’s theorem, discuss the structure of the proof in general terms, and then apply these ideas to the Dirac equation, a relativistic wave equation describing spin-<span class="latex-inline" data-latex="\tfrac{1}{2}">$\tfrac{1}{2}$</span> fermions.

---

**1. Introduction to Noether’s Theorem**

The link between symmetry and conservation laws was famously formalized by Emmy Noether in 1918. Prior to her work, conservation laws were understood empirically (e.g., conservation of energy, momentum, and angular momentum) but lacked a unifying explanation. Noether’s theorem bridges this gap by showing that each continuous symmetry of a system’s action corresponds to a conserved quantity.

**Key Concepts:**

1. **Action Functional:** In classical field theory, a system is described by fields <span class="latex-inline" data-latex="\phi(x)">$\phi(x)$</span> and an action <span class="latex-inline" data-latex="S[\phi]">$S[\phi]$</span>, which is defined as the integral of the Lagrangian density <span class="latex-inline" data-latex="\mathcal{L}(\phi, \partial_\mu \phi)">$\mathcal{L}(\phi, \partial_\mu \phi)$</span> over spacetime:
   <div class="latex-display" data-latex="
   S[\phi] = \int d^4x \,\mathcal{L}(\phi, \partial_\mu \phi).
   ">$$
   S[\phi] = \int d^4x \,\mathcal{L}(\phi, \partial_\mu \phi).
   $$</div>

2. **Symmetry Transformation:** A continuous symmetry is a continuous transformation of the fields <span class="latex-inline" data-latex="\phi \to \phi + \delta \phi(\epsilon)">$\phi \to \phi + \delta \phi(\epsilon)$</span> parameterized by a small parameter <span class="latex-inline" data-latex="\epsilon">$\epsilon$</span>, under which the action remains invariant (or changes by a total derivative, which does not affect the equations of motion). Typical examples include global phase rotations of complex fields, spacetime translations, and Lorentz transformations.

3. **Conservation Laws:** Noether’s theorem provides a systematic procedure for constructing a conserved current <span class="latex-inline" data-latex="j^\mu">$j^\mu$</span> associated with each continuous symmetry. The conservation law is expressed as <span class="latex-inline" data-latex="\partial_\mu j^\mu = 0">$\partial_\mu j^\mu = 0$</span>, and the conserved charge is obtained by integrating the time-component of the current over all space:
   <div class="latex-display" data-latex="
   Q = \int d^3x \, j^0(t,\vec{x}).
   ">$$
   Q = \int d^3x \, j^0(t,\vec{x}).
   $$</div>

---

**2. Sketch of Noether’s Theorem Proof**

Consider a continuous symmetry transformation on the fields:
<div class="latex-display" data-latex="
\phi(x) \to \phi'(x) = \phi(x) + \delta \phi(x),
">$$
\phi(x) \to \phi'(x) = \phi(x) + \delta \phi(x),
$$</div>
where <span class="latex-inline" data-latex="\delta \phi(x)">$\delta \phi(x)$</span> is small and depends linearly on a continuous parameter <span class="latex-inline" data-latex="\epsilon">$\epsilon$</span>.

The action under this transformation changes as:
<div class="latex-display" data-latex="
S[\phi'] = \int d^4x \,\mathcal{L}(\phi', \partial_\mu \phi').
">$$
S[\phi'] = \int d^4x \,\mathcal{L}(\phi', \partial_\mu \phi').
$$</div>

If the transformation is a symmetry, the variation of the action vanishes up to a total derivative:
<div class="latex-display" data-latex="
\delta S = \int d^4x \left(\frac{\partial \mathcal{L}}{\partial \phi} \delta \phi + \frac{\partial \mathcal{L}}{\partial (\partial_\mu \phi)} \delta (\partial_\mu \phi) \right) = \int d^4x\, \partial_\mu F^\mu(\phi, \delta\phi),
">$$
\delta S = \int d^4x \left(\frac{\partial \mathcal{L}}{\partial \phi} \delta \phi + \frac{\partial \mathcal{L}}{\partial (\partial_\mu \phi)} \delta (\partial_\mu \phi) \right) = \int d^4x\, \partial_\mu F^\mu(\phi, \delta\phi),
$$</div>
where <span class="latex-inline" data-latex="F^\mu">$F^\mu$</span> is some four-vector function constructed from the fields and their variations. Because total derivatives do not affect the equations of motion, the physical content of the theory is invariant.

Using the Euler-Lagrange equations for fields,
<div class="latex-display" data-latex="
\frac{\partial \mathcal{L}}{\partial \phi} - \partial_\mu \left( \frac{\partial \mathcal{L}}{\partial (\partial_\mu \phi)} \right) = 0,
">$$
\frac{\partial \mathcal{L}}{\partial \phi} - \partial_\mu \left( \frac{\partial \mathcal{L}}{\partial (\partial_\mu \phi)} \right) = 0,
$$</div>
we can rearrange terms to identify a conserved current. After some algebra, one finds a current <span class="latex-inline" data-latex="j^\mu">$j^\mu$</span> such that:
<div class="latex-display" data-latex="
\partial_\mu j^\mu = 0.
">$$
\partial_\mu j^\mu = 0.
$$</div>

The main steps in the proof are:

1. **Vary the Action:** Compute <span class="latex-inline" data-latex="\delta S">$\delta S$</span> under the field variation <span class="latex-inline" data-latex="\delta \phi">$\delta \phi$</span>.
2. **Use the Euler-Lagrange Equations:** Replace terms involving <span class="latex-inline" data-latex="\frac{\partial \mathcal{L}}{\partial \phi}">$\frac{\partial \mathcal{L}}{\partial \phi}$</span> using the equations of motion so that all non-vanishing contributions reduce to a total derivative.
3. **Identify the Conserved Current:** The remainder defines the Noether current <span class="latex-inline" data-latex="j^\mu">$j^\mu$</span>.

In a nutshell, the proof shows that from a continuous symmetry of the action, one can extract a corresponding conserved current and charge.

---

**3. The Dirac Equation and Its Lagrangian**

The Dirac equation describes relativistic spin-<span class="latex-inline" data-latex="\tfrac{1}{2}">$\tfrac{1}{2}$</span> fermions (e.g., electrons). The Dirac field <span class="latex-inline" data-latex="\psi(x)">$\psi(x)$</span> is a spinor field, and the Dirac Lagrangian density is given by:
<div class="latex-display" data-latex="
\mathcal{L} = \bar{\psi}(x) (i\gamma^\mu \partial_\mu - m) \psi(x),
">$$
\mathcal{L} = \bar{\psi}(x) (i\gamma^\mu \partial_\mu - m) \psi(x),
$$</div>
where <span class="latex-inline" data-latex="\bar{\psi} = \psi^\dagger \gamma^0">$\bar{\psi} = \psi^\dagger \gamma^0$</span>, and <span class="latex-inline" data-latex="\gamma^\mu">$\gamma^\mu$</span> are the gamma matrices satisfying the Clifford algebra <span class="latex-inline" data-latex="\{\gamma^\mu, \gamma^\nu\} = 2\eta^{\mu\nu}">$\{\gamma^\mu, \gamma^\nu\} = 2\eta^{\mu\nu}$</span>.

The Euler-Lagrange equations for <span class="latex-inline" data-latex="\psi">$\psi$</span> yield the Dirac equation:
<div class="latex-display" data-latex="
(i\gamma^\mu \partial_\mu - m)\psi(x) = 0.
">$$
(i\gamma^\mu \partial_\mu - m)\psi(x) = 0.
$$</div>

**Common Symmetries of the Dirac Lagrangian:**

1. **Global Phase Symmetry (U(1) symmetry):**  
   Consider the global phase transformation <span class="latex-inline" data-latex="\psi(x) \to e^{i\alpha}\psi(x)">$\psi(x) \to e^{i\alpha}\psi(x)$</span>, where <span class="latex-inline" data-latex="\alpha">$\alpha$</span> is a constant parameter. Under this transformation, <span class="latex-inline" data-latex="\bar{\psi}(x)">$\bar{\psi}(x)$</span> transforms as <span class="latex-inline" data-latex="\bar{\psi}(x) \to \bar{\psi}(x)e^{-i\alpha}">$\bar{\psi}(x) \to \bar{\psi}(x)e^{-i\alpha}$</span>. The Dirac Lagrangian is invariant under this global U(1) transformation because the mass term <span class="latex-inline" data-latex="\bar{\psi}\psi">$\bar{\psi}\psi$</span> and the kinetic term <span class="latex-inline" data-latex="\bar{\psi}i\gamma^\mu\partial_\mu\psi">$\bar{\psi}i\gamma^\mu\partial_\mu\psi$</span> are both invariant under a global phase (no spacetime dependence of <span class="latex-inline" data-latex="\alpha">$\alpha$</span>).

2. **Lorentz Symmetry:**  
   The Dirac equation is constructed to be invariant under Lorentz transformations. However, let us focus on the simpler U(1) global symmetry to see Noether’s theorem in action.

---

**4. Applying Noether’s Theorem to the Dirac Equation**

**Step-by-Step Application:**

1. **Identify the Symmetry:**  
   We have the global phase transformation:
   <div class="latex-display" data-latex="
   \psi(x) \to \psi'(x) = e^{i\alpha}\psi(x), \quad \bar{\psi}(x) \to \bar{\psi}'(x) = \bar{\psi}(x)e^{-i\alpha}.
   ">$$
   \psi(x) \to \psi'(x) = e^{i\alpha}\psi(x), \quad \bar{\psi}(x) \to \bar{\psi}'(x) = \bar{\psi}(x)e^{-i\alpha}.
   $$</div>
   For an infinitesimal transformation <span class="latex-inline" data-latex="\alpha">$\alpha$</span> small, we write:
   <div class="latex-display" data-latex="
   \delta \psi = i\alpha \psi, \quad \delta \bar{\psi} = -i\alpha \bar{\psi}.
   ">$$
   \delta \psi = i\alpha \psi, \quad \delta \bar{\psi} = -i\alpha \bar{\psi}.
   $$</div>

2. **Vary the Action:**  
   The Lagrangian transforms as:
   <div class="latex-display" data-latex="
   \delta \mathcal{L} = \frac{\partial \mathcal{L}}{\partial \psi}\delta \psi + \frac{\partial \mathcal{L}}{\partial \bar{\psi}}\delta \bar{\psi}.
   ">$$
   \delta \mathcal{L} = \frac{\partial \mathcal{L}}{\partial \psi}\delta \psi + \frac{\partial \mathcal{L}}{\partial \bar{\psi}}\delta \bar{\psi}.
   $$</div>
   Since the Lagrangian is invariant under the global U(1) (no explicit dependence on <span class="latex-inline" data-latex="\alpha">$\alpha$</span>), <span class="latex-inline" data-latex="\delta \mathcal{L} = 0">$\delta \mathcal{L} = 0$</span>.

3. **Noether Current Construction:**  
   The canonical Noether procedure tells us that the current associated with this symmetry is:
   <div class="latex-display" data-latex="
   j^\mu = \frac{\partial \mathcal{L}}{\partial (\partial_\mu \psi)}\delta \psi + \frac{\partial \mathcal{L}}{\partial (\partial_\mu \bar{\psi})}\delta \bar{\psi}.
   ">$$
   j^\mu = \frac{\partial \mathcal{L}}{\partial (\partial_\mu \psi)}\delta \psi + \frac{\partial \mathcal{L}}{\partial (\partial_\mu \bar{\psi})}\delta \bar{\psi}.
   $$</div>

   For the Dirac Lagrangian, we have:
   <div class="latex-display" data-latex="
   \frac{\partial \mathcal{L}}{\partial (\partial_\mu \psi)} = \bar{\psi}i\gamma^\mu, \quad \frac{\partial \mathcal{L}}{\partial (\partial_\mu \bar{\psi})} = 0,
   ">$$
   \frac{\partial \mathcal{L}}{\partial (\partial_\mu \psi)} = \bar{\psi}i\gamma^\mu, \quad \frac{\partial \mathcal{L}}{\partial (\partial_\mu \bar{\psi})} = 0,
   $$</div>
   because <span class="latex-inline" data-latex="\mathcal{L}">$\mathcal{L}$</span> depends on <span class="latex-inline" data-latex="\partial_\mu \psi">$\partial_\mu \psi$</span> but not on <span class="latex-inline" data-latex="\partial_\mu \bar{\psi}">$\partial_\mu \bar{\psi}$</span> (only on <span class="latex-inline" data-latex="\bar{\psi}">$\bar{\psi}$</span> itself).

   Therefore:
   <div class="latex-display" data-latex="
   j^\mu = \bar{\psi} i\gamma^\mu (i\alpha\psi) = \alpha \bar{\psi}\gamma^\mu \psi.
   ">$$
   j^\mu = \bar{\psi} i\gamma^\mu (i\alpha\psi) = \alpha \bar{\psi}\gamma^\mu \psi.
   $$</div>

   Since <span class="latex-inline" data-latex="\alpha">$\alpha$</span> is just the infinitesimal parameter, the conserved current (dropping the factor <span class="latex-inline" data-latex="\alpha">$\alpha$</span>) is identified as:
   <div class="latex-display" data-latex="
   j^\mu = \bar{\psi}\gamma^\mu \psi.
   ">$$
   j^\mu = \bar{\psi}\gamma^\mu \psi.
   $$</div>

4. **Conservation of the Current:**  
   To verify that this current is conserved, we use the Dirac equation. The conservation law is <span class="latex-inline" data-latex="\partial_\mu j^\mu = 0">$\partial_\mu j^\mu = 0$</span>. Starting from:
   <div class="latex-display" data-latex="
   j^\mu = \bar{\psi}\gamma^\mu \psi,
   ">$$
   j^\mu = \bar{\psi}\gamma^\mu \psi,
   $$</div>
   we take the derivative:
   <div class="latex-display" data-latex="
   \partial_\mu j^\mu = (\partial_\mu \bar{\psi})\gamma^\mu \psi + \bar{\psi}\gamma^\mu (\partial_\mu \psi).
   ">$$
   \partial_\mu j^\mu = (\partial_\mu \bar{\psi})\gamma^\mu \psi + \bar{\psi}\gamma^\mu (\partial_\mu \psi).
   $$</div>

   Using the Dirac equations <span class="latex-inline" data-latex="(i\gamma^\mu \partial_\mu - m)\psi=0">$(i\gamma^\mu \partial_\mu - m)\psi=0$</span> and <span class="latex-inline" data-latex="\bar{\psi}(i\gamma^\mu \overleftarrow{\partial_\mu} + m)=0">$\bar{\psi}(i\gamma^\mu \overleftarrow{\partial_\mu} + m)=0$</span> (the latter obtained by taking the adjoint and multiplying by <span class="latex-inline" data-latex="\gamma^0">$\gamma^0$</span>), one finds after some algebra that <span class="latex-inline" data-latex="\partial_\mu j^\mu = 0">$\partial_\mu j^\mu = 0$</span>.

**Result:**  
We have identified a conserved current <span class="latex-inline" data-latex="j^\mu">$j^\mu$</span> and the corresponding conserved charge:
<div class="latex-display" data-latex="
Q = \int d^3x \, j^0(x) = \int d^3x \, \psi^\dagger(x)\psi(x),
">$$
Q = \int d^3x \, j^0(x) = \int d^3x \, \psi^\dagger(x)\psi(x),
$$</div>
which physically corresponds to the total particle number (in many interpretations). This is a direct consequence of the global U(1) symmetry of the Dirac Lagrangian.

---

**5. Interpretation and General Significance**

Noether’s theorem provides a deep physical insight: the invariance of the Dirac action under global phase rotations ensures the conservation of a quantity that can be interpreted as the number of fermions described by the field. In the quantum theory, this relates to charge conservation and the existence of a conserved quantum number.

This same methodology extends to more complicated theories and more elaborate symmetry groups. Gauge symmetries lead to gauge currents and gauge charges, while spacetime symmetries yield conservation of energy-momentum and angular momentum.

---

**6. Conclusion**

Noether’s theorem is a powerful tool that elevates symmetry principles from aesthetic guidelines to engines of fundamental laws. In the context of the Dirac equation, it links the invariance of the Lagrangian under a simple global phase transformation to a physically meaningful conservation law: the conservation of fermion number. This example is emblematic of how Noether’s theorem operates across all quantum field theories, cementing symmetry as the heart of conservation laws and, by extension, the structure of the physical world.

---

**Further Reading:**

- E. Noether, “Invariante Variationsprobleme,” Nachr. König. Gesellsch. Wiss. Göttingen, Math-Phys. Kl., 235–257 (1918).
- L. H. Ryder, *Quantum Field Theory*, 2nd edition (Cambridge University Press, 1996).
- P. Ramond, *Field Theory: A Modern Primer* (Addison-Wesley, 1990).

These references provide more rigorous discussions of Noether’s theorem and detailed treatments of the Dirac equation and its symmetries.

---


<!-- LATEX_PROTECTION_END -->

---
*Chapter 5 of "Noether Theorem Conversations" | Generated by Humanizer Lighthouse*
*Protected LaTeX content with fallback formatting*
