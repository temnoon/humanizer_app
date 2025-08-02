# Chapter 3: Noether Theorem and Dirac


*Conversation from December 05, 2024*

## Message 1

Give me an article explaining the proof of Noether's theorem (not necessarily displaying the entire proof) and applying it to the example of the Dirac equation.

---

## Message 2

**Title: Noether’s Theorem and Its Application to the Dirac Equation**

**Abstract:**  
Noether’s theorem is a cornerstone of modern theoretical physics, forging a profound connection between the symmetries of a physical system and its conservation laws. In essence, it states that for every continuous symmetry of the action of a physical system, there is a corresponding conserved current and an associated conserved quantity. This result is foundational in classical and quantum field theories, providing a unifying framework for understanding why certain quantities remain invariant under time evolution. In this article, we first outline the conceptual setting and main steps of Noether’s theorem, discuss the structure of the proof in general terms, and then apply these ideas to the Dirac equation, a relativistic wave equation describing spin-\(\tfrac{1}{2}\) fermions.

---

**1. Introduction to Noether’s Theorem**

The link between symmetry and conservation laws was famously formalized by Emmy Noether in 1918. Prior to her work, conservation laws were understood empirically (e.g., conservation of energy, momentum, and angular momentum) but lacked a unifying explanation. Noether’s theorem bridges this gap by showing that each continuous symmetry of a system’s action corresponds to a conserved quantity.

**Key Concepts:**

1. **Action Functional:** In classical field theory, a system is described by fields \(\phi(x)\) and an action \(S[\phi]\), which is defined as the integral of the Lagrangian density \(\mathcal{L}(\phi, \partial_\mu \phi)\) over spacetime:
   \[
   S[\phi] = \int d^4x \,\mathcal{L}(\phi, \partial_\mu \phi).
   \]

2. **Symmetry Transformation:** A continuous symmetry is a continuous transformation of the fields \(\phi \to \phi + \delta \phi(\epsilon)\) parameterized by a small parameter \(\epsilon\), under which the action remains invariant (or changes by a total derivative, which does not affect the equations of motion). Typical examples include global phase rotations of complex fields, spacetime translations, and Lorentz transformations.

3. **Conservation Laws:** Noether’s theorem provides a systematic procedure for constructing a conserved current \(j^\mu\) associated with each continuous symmetry. The conservation law is expressed as \(\partial_\mu j^\mu = 0\), and the conserved charge is obtained by integrating the time-component of the current over all space:
   \[
   Q = \int d^3x \, j^0(t,\vec{x}).
   \]

---

**2. Sketch of Noether’s Theorem Proof**

Consider a continuous symmetry transformation on the fields:
\[
\phi(x) \to \phi'(x) = \phi(x) + \delta \phi(x),
\]
where \(\delta \phi(x)\) is small and depends linearly on a continuous parameter \(\epsilon\).

The action under this transformation changes as:
\[
S[\phi'] = \int d^4x \,\mathcal{L}(\phi', \partial_\mu \phi').
\]

If the transformation is a symmetry, the variation of the action vanishes up to a total derivative:
\[
\delta S = \int d^4x \left(\frac{\partial \mathcal{L}}{\partial \phi} \delta \phi + \frac{\partial \mathcal{L}}{\partial (\partial_\mu \phi)} \delta (\partial_\mu \phi) \right) = \int d^4x\, \partial_\mu F^\mu(\phi, \delta\phi),
\]
where \(F^\mu\) is some four-vector function constructed from the fields and their variations. Because total derivatives do not affect the equations of motion, the physical content of the theory is invariant.

Using the Euler-Lagrange equations for fields,
\[
\frac{\partial \mathcal{L}}{\partial \phi} - \partial_\mu \left( \frac{\partial \mathcal{L}}{\partial (\partial_\mu \phi)} \right) = 0,
\]
we can rearrange terms to identify a conserved current. After some algebra, one finds a current \(j^\mu\) such that:
\[
\partial_\mu j^\mu = 0.
\]

The main steps in the proof are:

1. **Vary the Action:** Compute \(\delta S\) under the field variation \(\delta \phi\).
2. **Use the Euler-Lagrange Equations:** Replace terms involving \(\frac{\partial \mathcal{L}}{\partial \phi}\) using the equations of motion so that all non-vanishing contributions reduce to a total derivative.
3. **Identify the Conserved Current:** The remainder defines the Noether current \(j^\mu\).

In a nutshell, the proof shows that from a continuous symmetry of the action, one can extract a corresponding conserved current and charge.

---

**3. The Dirac Equation and Its Lagrangian**

The Dirac equation describes relativistic spin-\(\tfrac{1}{2}\) fermions (e.g., electrons). The Dirac field \(\psi(x)\) is a spinor field, and the Dirac Lagrangian density is given by:
\[
\mathcal{L} = \bar{\psi}(x) (i\gamma^\mu \partial_\mu - m) \psi(x),
\]
where \(\bar{\psi} = \psi^\dagger \gamma^0\), and \(\gamma^\mu\) are the gamma matrices satisfying the Clifford algebra \(\{\gamma^\mu, \gamma^\nu\} = 2\eta^{\mu\nu}\).

The Euler-Lagrange equations for \(\psi\) yield the Dirac equation:
\[
(i\gamma^\mu \partial_\mu - m)\psi(x) = 0.
\]

**Common Symmetries of the Dirac Lagrangian:**

1. **Global Phase Symmetry (U(1) symmetry):**  
   Consider the global phase transformation \(\psi(x) \to e^{i\alpha}\psi(x)\), where \(\alpha\) is a constant parameter. Under this transformation, \(\bar{\psi}(x)\) transforms as \(\bar{\psi}(x) \to \bar{\psi}(x)e^{-i\alpha}\). The Dirac Lagrangian is invariant under this global U(1) transformation because the mass term \(\bar{\psi}\psi\) and the kinetic term \(\bar{\psi}i\gamma^\mu\partial_\mu\psi\) are both invariant under a global phase (no spacetime dependence of \(\alpha\)).

2. **Lorentz Symmetry:**  
   The Dirac equation is constructed to be invariant under Lorentz transformations. However, let us focus on the simpler U(1) global symmetry to see Noether’s theorem in action.

---

**4. Applying Noether’s Theorem to the Dirac Equation**

**Step-by-Step Application:**

1. **Identify the Symmetry:**  
   We have the global phase transformation:
   \[
   \psi(x) \to \psi'(x) = e^{i\alpha}\psi(x), \quad \bar{\psi}(x) \to \bar{\psi}'(x) = \bar{\psi}(x)e^{-i\alpha}.
   \]
   For an infinitesimal transformation \(\alpha\) small, we write:
   \[
   \delta \psi = i\alpha \psi, \quad \delta \bar{\psi} = -i\alpha \bar{\psi}.
   \]

2. **Vary the Action:**  
   The Lagrangian transforms as:
   \[
   \delta \mathcal{L} = \frac{\partial \mathcal{L}}{\partial \psi}\delta \psi + \frac{\partial \mathcal{L}}{\partial \bar{\psi}}\delta \bar{\psi}.
   \]
   Since the Lagrangian is invariant under the global U(1) (no explicit dependence on \(\alpha\)), \(\delta \mathcal{L} = 0\).

3. **Noether Current Construction:**  
   The canonical Noether procedure tells us that the current associated with this symmetry is:
   \[
   j^\mu = \frac{\partial \mathcal{L}}{\partial (\partial_\mu \psi)}\delta \psi + \frac{\partial \mathcal{L}}{\partial (\partial_\mu \bar{\psi})}\delta \bar{\psi}.
   \]

   For the Dirac Lagrangian, we have:
   \[
   \frac{\partial \mathcal{L}}{\partial (\partial_\mu \psi)} = \bar{\psi}i\gamma^\mu, \quad \frac{\partial \mathcal{L}}{\partial (\partial_\mu \bar{\psi})} = 0,
   \]
   because \(\mathcal{L}\) depends on \(\partial_\mu \psi\) but not on \(\partial_\mu \bar{\psi}\) (only on \(\bar{\psi}\) itself).

   Therefore:
   \[
   j^\mu = \bar{\psi} i\gamma^\mu (i\alpha\psi) = \alpha \bar{\psi}\gamma^\mu \psi.
   \]

   Since \(\alpha\) is just the infinitesimal parameter, the conserved current (dropping the factor \(\alpha\)) is identified as:
   \[
   j^\mu = \bar{\psi}\gamma^\mu \psi.
   \]

4. **Conservation of the Current:**  
   To verify that this current is conserved, we use the Dirac equation. The conservation law is \(\partial_\mu j^\mu = 0\). Starting from:
   \[
   j^\mu = \bar{\psi}\gamma^\mu \psi,
   \]
   we take the derivative:
   \[
   \partial_\mu j^\mu = (\partial_\mu \bar{\psi})\gamma^\mu \psi + \bar{\psi}\gamma^\mu (\partial_\mu \psi).
   \]

   Using the Dirac equations \((i\gamma^\mu \partial_\mu - m)\psi=0\) and \(\bar{\psi}(i\gamma^\mu \overleftarrow{\partial_\mu} + m)=0\) (the latter obtained by taking the adjoint and multiplying by \(\gamma^0\)), one finds after some algebra that \(\partial_\mu j^\mu = 0\).

**Result:**  
We have identified a conserved current \(j^\mu\) and the corresponding conserved charge:
\[
Q = \int d^3x \, j^0(x) = \int d^3x \, \psi^\dagger(x)\psi(x),
\]
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


---
*Chapter 5 of "Noether Theorem Conversations" | Generated by Humanizer Lighthouse*
*Raw LaTeX content - processed by Enhanced LaTeX Plugin*
