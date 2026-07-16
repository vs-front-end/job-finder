export type TitlePreset = {
  id: string;
  label: string;
  patterns: string[];
};

export const rolePresets: TitlePreset[] = [
  { id: 'software-engineer', label: 'Software Engineer', patterns: ['software.*engineer', 'software.*developer'] },
  { id: 'frontend', label: 'Frontend', patterns: ['front.?end'] },
  { id: 'backend', label: 'Backend', patterns: ['back.?end'] },
  { id: 'fullstack', label: 'Full Stack', patterns: ['full.?stack'] },
  { id: 'web', label: 'Web Developer', patterns: ['web.*(?:developer|engineer)'] },
  { id: 'mobile', label: 'Mobile', patterns: ['mobile.*(?:developer|engineer)'] },
  { id: 'react', label: 'React / React Native', patterns: ['react(?: native)?.*(?:developer|engineer)'] },
  { id: 'ts-js', label: 'TypeScript / JavaScript', patterns: ['(?:typescript|javascript).*(?:developer|engineer)'] },
  { id: 'devops', label: 'DevOps / SRE', patterns: ['\\bdevops\\b', 'site reliability'] },
  { id: 'platform-cloud', label: 'Platform / Cloud', patterns: ['platform engineer', 'cloud engineer', 'infrastructure engineer'] },
  { id: 'data', label: 'Data Engineer', patterns: ['data engineer'] },
  { id: 'ml-ai', label: 'ML / AI', patterns: ['machine learning', '\\bml engineer'] },
  { id: 'qa', label: 'QA / Testing', patterns: ['\\bqa\\b', 'quality assurance', '\\btest(?:ing)? engineer'] },
  { id: 'security', label: 'Security', patterns: ['security engineer'] },
  { id: 'game', label: 'Game Developer', patterns: ['game.*(?:developer|engineer)'] },
];

export const exclusionPresets: TitlePreset[] = [
  { id: 'senior', label: 'Senior', patterns: ['\\b(?:senior|sr)\\b\\.?'] },
  { id: 'staff', label: 'Staff', patterns: ['\\bstaff\\b'] },
  { id: 'principal', label: 'Principal / Distinguished', patterns: ['\\bprincipal\\b', '\\bdistinguished\\b'] },
  { id: 'lead', label: 'Lead / Head / Chief', patterns: ['\\blead\\b', '\\bhead\\b', '\\bchief\\b'] },
  { id: 'management', label: 'Manager / Director / VP', patterns: ['\\bmanager\\b', '\\bdirector\\b', '\\bvp\\b'] },
  { id: 'architect', label: 'Architect', patterns: ['\\barchitect\\b'] },
  { id: 'specialist', label: 'Specialist', patterns: ['\\b(?:specialist|spec)\\b'] },
  { id: 'junior', label: 'Junior', patterns: ['\\b(?:junior|jr)\\b\\.?'] },
  { id: 'intern', label: 'Intern', patterns: ['\\bintern(ship)?\\b'] },
  { id: 'backend', label: 'Backend-only', patterns: ['back.?end'] },
  { id: 'devops', label: 'DevOps / SRE', patterns: ['\\bdevops\\b', 'site reliability'] },
  { id: 'platform-cloud', label: 'Platform / Cloud / Infra', patterns: ['platform engineer', 'cloud engineer', 'infrastructure engineer'] },
  { id: 'data-ml', label: 'Data / ML', patterns: ['data engineer', 'machine learning', '\\bml engineer'] },
  { id: 'qa', label: 'QA / Testing', patterns: ['\\bqa\\b', 'quality assurance', '\\btest(?:ing)? engineer'] },
  { id: 'security', label: 'Security', patterns: ['security engineer'] },
];

export const technologySuggestions = [
  'React',
  'React Native',
  'TypeScript',
  'JavaScript',
  'Vue',
  'Angular',
  'Svelte',
  'Next.js',
  'Node.js',
  'Python',
  'Django',
  'FastAPI',
  'Go',
  'Rust',
  'Java',
  'Kotlin',
  'Spring',
  'Swift',
  'C#',
  '.NET',
  'PHP',
  'Laravel',
  'Ruby',
  'Rails',
  'Elixir',
  'Flutter',
  'GraphQL',
  'PostgreSQL',
  'AWS',
  'Docker',
  'Kubernetes',
];

export const languageOptions = [
  { code: 'en', label: 'English' },
  { code: 'pt', label: 'Portuguese' },
  { code: 'es', label: 'Spanish' },
  { code: 'de', label: 'German' },
  { code: 'fr', label: 'French' },
];

export const countryOptions = [
  { code: 'AR', label: 'Argentina' },
  { code: 'AU', label: 'Australia' },
  { code: 'BR', label: 'Brazil' },
  { code: 'CA', label: 'Canada' },
  { code: 'CL', label: 'Chile' },
  { code: 'CO', label: 'Colombia' },
  { code: 'CZ', label: 'Czechia' },
  { code: 'DE', label: 'Germany' },
  { code: 'DK', label: 'Denmark' },
  { code: 'ES', label: 'Spain' },
  { code: 'FI', label: 'Finland' },
  { code: 'FR', label: 'France' },
  { code: 'GB', label: 'United Kingdom' },
  { code: 'GR', label: 'Greece' },
  { code: 'IE', label: 'Ireland' },
  { code: 'IN', label: 'India' },
  { code: 'IT', label: 'Italy' },
  { code: 'MX', label: 'Mexico' },
  { code: 'NG', label: 'Nigeria' },
  { code: 'NL', label: 'Netherlands' },
  { code: 'NO', label: 'Norway' },
  { code: 'NZ', label: 'New Zealand' },
  { code: 'PE', label: 'Peru' },
  { code: 'PH', label: 'Philippines' },
  { code: 'PL', label: 'Poland' },
  { code: 'PT', label: 'Portugal' },
  { code: 'RO', label: 'Romania' },
  { code: 'SE', label: 'Sweden' },
  { code: 'TR', label: 'Turkey' },
  { code: 'UA', label: 'Ukraine' },
  { code: 'US', label: 'United States' },
  { code: 'UY', label: 'Uruguay' },
  { code: 'ZA', label: 'South Africa' },
];

export const timezoneOptions = Array.from({ length: 27 }, (_, index) => {
  const offset = index - 12;
  return offset >= 0 ? `UTC+${offset}` : `UTC${offset}`;
});

export const currencySuggestions = ['BRL', 'ARS', 'MXN', 'INR', 'TRY', 'UAH', 'PHP', 'NGN'];

export const maxAgeOptions = [1, 2, 3, 5, 7, 14, 30];
