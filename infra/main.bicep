// Static Web App du lab (D-040, D-045). Déployée par Claude Code avec le compte claude-ai-dynamic,
// dans rg-ai-dynamic-poc (abonnement sandbox-ai-dynamic) :
//   az deployment group what-if -g rg-ai-dynamic-poc -f infra/main.bicep
//   az deployment group create  -g rg-ai-dynamic-poc -f infra/main.bicep
// Plan Free (Policy lab-swa-free-only), Central US (Static Web Apps absent de France Central).
// stagingEnvironmentPolicy Disabled : pas d'environnement d'aperçu public pour les PR.

param location string = 'centralus'

resource site 'Microsoft.Web/staticSites@2024-04-01' = {
  name: 'swa-ai-dynamic-lab'
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    stagingEnvironmentPolicy: 'Disabled'
    allowConfigFileUpdates: true
    #disable-next-line BCP037 // propriété acceptée par ARM, absente du schéma Bicep 0.49.2
    deploymentAuthPolicy: 'DeploymentToken'
    repositoryUrl: 'https://github.com/cristalcorp/lab-site'
    branch: 'main'
    provider: 'GitHub'
  }
}

output hote string = site.properties.defaultHostname
