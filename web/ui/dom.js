// Tiny helpers for building page elements safely (all text goes in as text, never as HTML).

function fill(el, attrs, kids) {
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === false || v === null || v === undefined) continue;
    if (k === 'class') el.setAttribute('class', v);
    else el.setAttribute(k, v === true ? '' : String(v));
  }
  for (const kid of kids.flat(Infinity)) {
    if (kid === null || kid === undefined || kid === false) continue;
    el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return el;
}

/** Make an HTML element: h('p', {class: 'x'}, 'text', child). */
export function h(tag, attrs, ...kids) {
  return fill(document.createElement(tag), attrs, kids);
}

/** Make an SVG element. */
export function s(tag, attrs, ...kids) {
  return fill(document.createElementNS('http://www.w3.org/2000/svg', tag), attrs, kids);
}

/** A source-label chip such as COUNT, RA, BOOK, GK. */
export function chip(label) {
  return h('span', { class: label.length > 8 ? 'chip long' : 'chip', title: 'Source label' }, label);
}

export function byId(id) {
  return document.getElementById(id);
}
