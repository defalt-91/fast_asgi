import * as fromUserFeatureStore from './user-feature-store.actions';

describe('loadUserFeatureStores', () => {
  it('should return an action', () => {
    expect(fromUserFeatureStore.userAccess().type).toBe('[userAccess] Load userAccess');
  });
});
