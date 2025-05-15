import Modal from "bootstrap/js/dist/modal";

export const modal = (selector: string) => Modal.getOrCreateInstance(selector);

export function clone<T>(obj: T) {
	return JSON.parse(JSON.stringify(obj));
}
