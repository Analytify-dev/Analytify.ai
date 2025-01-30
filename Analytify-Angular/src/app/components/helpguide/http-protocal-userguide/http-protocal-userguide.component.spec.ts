import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HttpProtocalUserguideComponent } from './http-protocal-userguide.component';

describe('HttpProtocalUserguideComponent', () => {
  let component: HttpProtocalUserguideComponent;
  let fixture: ComponentFixture<HttpProtocalUserguideComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HttpProtocalUserguideComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(HttpProtocalUserguideComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});