export function mensajeAuth(error: any): string {
  switch (error?.code) {
    case 'auth/email-already-in-use':
      return 'Ese correo ya tiene una cuenta. Intenta iniciar sesión.';
    case 'auth/invalid-email':
      return 'El correo no tiene un formato válido.';
    case 'auth/weak-password':
      return 'La contraseña es muy débil. Usa al menos 6 caracteres.';
    case 'auth/invalid-credential':
    case 'auth/wrong-password':
    case 'auth/user-not-found':
      return 'Correo o contraseña incorrectos.';
    case 'auth/too-many-requests':
      return 'Demasiados intentos. Espera unos minutos e inténtalo de nuevo.';
    case 'auth/network-request-failed':
      return 'Sin conexión. Revisa tu internet.';
    default:
      return 'Ocurrió un error. Inténtalo de nuevo.';
  }
}